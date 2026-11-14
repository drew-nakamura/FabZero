`timescale 1ns/1ps
module tb;
 parameter N=8;
 parameter LANES=1;
 reg clk=0, reset=1, start=0, load=0, operand_b=0;
 reg [15:0] address=0;
 reg signed [7:0] data_in=0;
 wire busy,done;
 wire [63:0] cycles;
 wire signed [31:0] data_out;
 reg [7:0] inputs [0:2*N*N-1];
 integer i;
 matmul #(.N(N),.LANES(LANES)) dut(.*);
 always #5 clk=~clk;
 initial begin
   $readmemh("inputs.hex",inputs);
   repeat(3) @(negedge clk);
   reset=0;
   for(i=0;i<2*N*N;i=i+1) begin
     load=1; operand_b=(i>=N*N); address=i%(N*N); data_in=inputs[i];
     @(negedge clk);
   end
   load=0; start=1;
   @(negedge clk); start=0;
   wait(done); @(negedge clk);
   $display("CYCLES %0d",cycles);
   for(i=0;i<N*N;i=i+1) begin
     address=i; #1; $display("OUT %0d",data_out);
   end
   $finish;
 end
 initial begin #1000000; $fatal(1,"timeout"); end
endmodule
