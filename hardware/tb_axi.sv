`timescale 1ns/1ps
module tb_axi;
 parameter N=8, LANES=1, INPUT_BITS=8;
 reg aclk=0,aresetn=0;
 reg [7:0] s_axi_awaddr=0,s_axi_araddr=0;
 reg s_axi_awvalid=0,s_axi_wvalid=0,s_axi_bready=0,s_axi_arvalid=0,s_axi_rready=0;
 reg [31:0] s_axi_wdata=0;
 reg [3:0] s_axi_wstrb=0;
 wire s_axi_awready,s_axi_wready,s_axi_bvalid,s_axi_arready,s_axi_rvalid;
 wire [1:0] s_axi_bresp,s_axi_rresp;
 wire [31:0] s_axi_rdata;
 integer i,j,expected;
 reg [31:0] value;
 matmul_axi #(.N(N),.LANES(LANES),.INPUT_BITS(INPUT_BITS)) dut(.*);
 always #5 aclk=~aclk;
 task send_aw(input [7:0] addr,input integer delay_cycles);
   begin
     repeat(delay_cycles) @(negedge aclk);
     @(negedge aclk); s_axi_awaddr=addr; s_axi_awvalid=1;
     @(posedge aclk); while(!s_axi_awready) @(posedge aclk);
     @(negedge aclk); s_axi_awvalid=0;
   end
 endtask
 task send_w(input [31:0] data,input [3:0] strb,input integer delay_cycles);
   begin
     repeat(delay_cycles) @(negedge aclk);
     @(negedge aclk); s_axi_wdata=data; s_axi_wstrb=strb; s_axi_wvalid=1;
     @(posedge aclk); while(!s_axi_wready) @(posedge aclk);
     @(negedge aclk); s_axi_wvalid=0;
   end
 endtask
 task write_reg(input [7:0] addr,input [31:0] data,input [3:0] strb,input integer order,input [1:0] response);
   begin
     fork
       send_aw(addr,(order==1)?3:0);
       send_w(data,strb,(order==2)?3:0);
     join
     while(!s_axi_bvalid) @(negedge aclk);
     repeat(3) begin
       if(!s_axi_bvalid || s_axi_bresp!==response || s_axi_awready || s_axi_wready)
         $fatal(1,"write response/backpressure addr=%h response=%h expected=%h",addr,s_axi_bresp,response);
       @(negedge aclk);
     end
     s_axi_bready=1; @(negedge aclk); s_axi_bready=0;
   end
 endtask
 task read_reg(input [7:0] addr,input [1:0] response,output [31:0] data);
   begin
     @(negedge aclk); s_axi_araddr=addr; s_axi_arvalid=1;
     @(posedge aclk); while(!s_axi_arready) @(posedge aclk);
     @(negedge aclk); s_axi_arvalid=0;
     while(!s_axi_rvalid) @(negedge aclk);
     data=s_axi_rdata;
     repeat(3) begin
       if(!s_axi_rvalid || s_axi_rresp!==response || s_axi_rdata!==data || s_axi_arready)
         $fatal(1,"read response/backpressure addr=%h",addr);
       @(negedge aclk);
     end
     s_axi_rready=1; @(negedge aclk); s_axi_rready=0;
   end
 endtask
 initial begin
   repeat(3) @(negedge aclk); aresetn=1;
   read_reg(0,0,value); if(value!==32'h53494c01) $fatal(1,"identity");
   read_reg(8'h20,0,value); if(value!==N) $fatal(1,"compiled N");
   read_reg(8'h24,0,value); if(value!==LANES) $fatal(1,"compiled LANES");
   write_reg(8'h20,0,15,1,2); write_reg(8'h24,0,15,2,2);
   read_reg(8'h20,0,value); if(value!==N) $fatal(1,"N read-only");
   read_reg(8'h24,0,value); if(value!==LANES) $fatal(1,"LANES read-only");
   read_reg(8'h14,2,value); // outputs invalid until first completion
   write_reg(8'h0c,32'h12345678,4'b0101,1,0);
   read_reg(8'h0c,0,value); if(value!==32'h00340078) $fatal(1,"byte strobes");
   write_reg(8'h0c,32'hffffffff,0,2,0);
   read_reg(8'h0c,0,value); if(value!==32'h00340078) $fatal(1,"zero strobes");
   write_reg(8'h0c,65535,15,0,0);
   write_reg(8'h10,1,1,0,2); // invalid operand address
   write_reg(8'h00,1,15,0,2); read_reg(8'h03,2,value);
   for(i=0;i<2*N*N;i=i+1) begin
     write_reg(8'h0c,(i>=N*N?65536:0)+(i%(N*N)),15,i%3,0);
     // A is identity; B includes -128 and positive values.
     expected=(i<N*N)?((i/N==i%N)?1:0):((i-N*N)*37%256)-128;
     write_reg(8'h10,expected,1,(i+1)%3,0);
   end
   write_reg(8'h04,1,0,0,0); // no strobe: must not launch
   read_reg(8'h08,0,value); if(value!==0) $fatal(1,"masked start");
   write_reg(8'h04,1,1,0,0);
   write_reg(8'h04,1,1,0,2);
   write_reg(8'h0c,0,15,0,2);
   write_reg(8'h10,127,1,0,2);
   read_reg(8'h18,2,value);
   read_reg(8'h08,0,value);
   while(!value[1]) read_reg(8'h08,0,value);
   if(value[0]) $fatal(1,"done busy");
   read_reg(8'h18,0,value); if(value!==N*N*N/LANES) $fatal(1,"cycles");
   read_reg(8'h1c,0,value); if(value!==0) $fatal(1,"cycles high");
   for(i=0;i<N*N;i=i+1) begin
     write_reg(8'h0c,i,15,i%3,0);
     read_reg(8'h14,0,value);
     expected=(i*37%256)-128;
     if($signed(value)!==expected) $fatal(1,"result index %0d got %0d expected %0d",i,$signed(value),expected);
   end
   // Read status on the edge that the kernel consumes a second start.
   // Previous sticky done must not leak into the new job's status.
   fork
     send_aw(8'h04,0);
     send_w(1,1,0);
   join
   while(!s_axi_bvalid) @(negedge aclk);
   s_axi_bready=1; s_axi_araddr=8'h08; s_axi_arvalid=1;
   @(posedge aclk);
   if(!s_axi_arready) $fatal(1,"second-start status readiness");
   @(negedge aclk); s_axi_bready=0; s_axi_arvalid=0;
   if(!s_axi_rvalid || s_axi_rresp!==0 || s_axi_rdata!==1)
     $fatal(1,"stale done leaked into restarted job status");
   s_axi_rready=1; @(negedge aclk); s_axi_rready=0;
   // Reset must discard a buffered AW without allowing a later W to pair with it.
   send_aw(8'h04,0);
   aresetn=0; @(negedge aclk); aresetn=1;
   send_w(1,1,0);
   repeat(4) @(negedge aclk);
   if(s_axi_bvalid) $fatal(1,"reset failed to flush address");
   aresetn=0; @(negedge aclk); aresetn=1;
   read_reg(8'h08,0,value); if(value!==0) $fatal(1,"reset status");
   $display("PASS AXI N=%0d LANES=%0d",N,LANES); $finish;
 end
 initial begin #10000000; $fatal(1,"timeout"); end
endmodule
