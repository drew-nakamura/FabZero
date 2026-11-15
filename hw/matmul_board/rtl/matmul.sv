// SiliconOS signed INT8 GEMM. LANES adjacent output columns per cycle.
// Flat local arrays are a functional first implementation, NOT a BRAM/DSP claim.
// Host loads operands while idle. Outputs remain valid until next job.
module matmul #(parameter N=8, parameter LANES=1)(
 input wire clk, reset, start, load,
 input wire operand_b,
 input wire [15:0] address,
 input wire signed [7:0] data_in,
 output reg busy, done,
 output reg [63:0] cycles,
 output wire signed [31:0] data_out
);
 reg signed [7:0] a [0:N*N-1];
 reg signed [7:0] b [0:N*N-1];
 reg signed [31:0] c [0:N*N-1];
 reg signed [31:0] acc [0:LANES-1];
 integer row, col, k, lane;
 wire signed [15:0] product [0:LANES-1];
 genvar g;
 generate for(g=0;g<LANES;g=g+1) begin: multipliers
   assign product[g] = a[row*N+k] * b[k*N+col+g];
 end endgenerate
 assign data_out = (address < N*N) ? c[address] : 32'sd0;
 always @(posedge clk) begin
   if(reset) begin
     busy<=0; done<=0; cycles<=0; row<=0; col<=0; k<=0;
     for(lane=0;lane<LANES;lane=lane+1) acc[lane]<=0;
   end else begin
     if(load && !busy && address < N*N) begin
       if(operand_b) b[address]<=data_in; else a[address]<=data_in;
     end
     if(start && !busy) begin
       busy<=1; done<=0; cycles<=0; row<=0; col<=0; k<=0;
       for(lane=0;lane<LANES;lane=lane+1) acc[lane]<=0;
     end else if(busy) begin
       cycles<=cycles+1;
       for(lane=0;lane<LANES;lane=lane+1) begin
         if(k==N-1) begin
           c[row*N+col+lane] <= acc[lane] + {{16{product[lane][15]}},product[lane]};
           acc[lane]<=0;
         end else acc[lane] <= acc[lane] + {{16{product[lane][15]}},product[lane]};
       end
       if(k==N-1) begin
         k<=0;
         if(col+LANES==N) begin
           col<=0;
           if(row==N-1) begin busy<=0; done<=1; end
           else row<=row+1;
         end else col<=col+LANES;
       end else k<=k+1;
     end
   end
 end
endmodule
