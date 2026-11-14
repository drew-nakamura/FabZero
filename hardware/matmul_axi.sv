// Generic 32-bit AXI4-Lite register slave. No board clock/reset/pin assumptions.
module matmul_axi #(parameter N=8, parameter LANES=1)(
 input wire aclk, aresetn,
 input wire [7:0] s_axi_awaddr,
 input wire s_axi_awvalid,
 output wire s_axi_awready,
 input wire [31:0] s_axi_wdata,
 input wire [3:0] s_axi_wstrb,
 input wire s_axi_wvalid,
 output wire s_axi_wready,
 output reg [1:0] s_axi_bresp,
 output reg s_axi_bvalid,
 input wire s_axi_bready,
 input wire [7:0] s_axi_araddr,
 input wire s_axi_arvalid,
 output wire s_axi_arready,
 output reg [31:0] s_axi_rdata,
 output reg [1:0] s_axi_rresp,
 output reg s_axi_rvalid,
 input wire s_axi_rready
);
 reg aw_pending, w_pending;
 reg [7:0] awaddr;
 reg [31:0] wdata, address_reg;
 reg [3:0] wstrb;
 reg start, load;
 reg signed [7:0] operand;
 wire busy,done;
 wire [63:0] cycles;
 wire signed [31:0] result;
 wire protected_busy = busy || start || load;
 integer byte_index;
 assign s_axi_awready=aresetn && !aw_pending && !s_axi_bvalid;
 assign s_axi_wready=aresetn && !w_pending && !s_axi_bvalid;
 assign s_axi_arready=aresetn && !s_axi_rvalid;
 matmul #(.N(N),.LANES(LANES)) kernel(
   .clk(aclk),.reset(!aresetn),.start(start),.load(load),
   .operand_b(address_reg[16]),.address(address_reg[15:0]),.data_in(operand),
   .busy(busy),.done(done),.cycles(cycles),.data_out(result));
 always @(posedge aclk) begin
   if(!aresetn) begin
     aw_pending<=0; w_pending<=0; awaddr<=0; wdata<=0; wstrb<=0;
     address_reg<=0; operand<=0; start<=0; load<=0;
     s_axi_bresp<=0; s_axi_bvalid<=0;
     s_axi_rdata<=0; s_axi_rresp<=0; s_axi_rvalid<=0;
   end else begin
     start<=0; load<=0;
     if(s_axi_bvalid && s_axi_bready) s_axi_bvalid<=0;
     if(s_axi_rvalid && s_axi_rready) s_axi_rvalid<=0;
     if(s_axi_awready && s_axi_awvalid) begin awaddr<=s_axi_awaddr; aw_pending<=1; end
     if(s_axi_wready && s_axi_wvalid) begin wdata<=s_axi_wdata; wstrb<=s_axi_wstrb; w_pending<=1; end
     if(aw_pending && w_pending && !s_axi_bvalid) begin
       aw_pending<=0; w_pending<=0; s_axi_bvalid<=1; s_axi_bresp<=0;
       case(awaddr)
         8'h04: begin
           if(wstrb[0] && wdata[0]) begin
             if(protected_busy) s_axi_bresp<=2'b10;
             else start<=1;
           end
         end
         8'h0c: begin
           if(protected_busy && |wstrb) s_axi_bresp<=2'b10;
           else for(byte_index=0;byte_index<4;byte_index=byte_index+1)
             if(wstrb[byte_index]) address_reg[8*byte_index+:8]<=wdata[8*byte_index+:8];
         end
         8'h10: begin
           if(wstrb[0]) begin
             if(protected_busy || address_reg[15:0]>=N*N) s_axi_bresp<=2'b10;
             else begin operand<=wdata[7:0]; load<=1; end
           end
         end
         default: s_axi_bresp<=2'b10;
       endcase
     end
     if(s_axi_arvalid && s_axi_arready) begin
       s_axi_rvalid<=1; s_axi_rresp<=0;
       case(s_axi_araddr)
         8'h00: s_axi_rdata<=32'h53494c01;
         8'h04: s_axi_rdata<=0;
         8'h20: s_axi_rdata<=N;
         8'h24: s_axi_rdata<=LANES;
         8'h08: s_axi_rdata<={30'b0,(done && !busy && !start),(busy || start)};
         8'h0c: s_axi_rdata<=address_reg;
         8'h10: s_axi_rdata<={24'b0,operand};
         8'h14: begin
           if(!done || busy || start) begin s_axi_rdata<=0; s_axi_rresp<=2'b10; end
           else s_axi_rdata<=result;
         end
         // Counters are readable only when stable, preventing torn 64-bit reads.
         8'h18: begin
           if(busy || start) begin s_axi_rdata<=0; s_axi_rresp<=2'b10; end
           else s_axi_rdata<=cycles[31:0];
         end
         8'h1c: begin
           if(busy || start) begin s_axi_rdata<=0; s_axi_rresp<=2'b10; end
           else s_axi_rdata<=cycles[63:32];
         end
         default: begin s_axi_rdata<=0; s_axi_rresp<=2'b10; end
       endcase
     end
   end
 end
endmodule
