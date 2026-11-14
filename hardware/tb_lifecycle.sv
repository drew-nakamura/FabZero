`timescale 1ns/1ps
// Independent protocol/arithmetic regression; does not consume application fixtures.
module tb_lifecycle;
 parameter N=8;
 parameter LANES=1;
 reg clk=0, reset=1, start=0, load=0, operand_b=0;
 reg [15:0] address=0;
 reg signed [7:0] data_in=0;
 wire busy, done;
 wire [63:0] cycles;
 wire signed [31:0] data_out;
 integer av[0:N*N-1], bv[0:N*N-1];
 integer i,j,k,expected,mode;
 matmul #(.N(N),.LANES(LANES)) dut(.*);
 always #5 clk=~clk;
 task load_operands(input integer pattern);
   begin
     for(i=0;i<N*N;i=i+1) begin
       if(pattern==0) begin av[i]=-128; bv[i]=-128; end
       else begin av[i]=((i*37+11)%256)-128; bv[i]=((i*53+7)%256)-128; end
     end
     for(i=0;i<2*N*N;i=i+1) begin
       load=1; operand_b=i>=N*N; address=i%(N*N);
       data_in=(i<N*N)?av[i]:bv[i-N*N];
       @(negedge clk);
     end
     load=0;
   end
 endtask
 task launch;
   begin
     start=1; @(negedge clk); start=0;
     if(!busy || done || cycles!==0) $fatal(1,"start protocol");
   end
 endtask
 task check_result;
   begin
     wait(done); @(negedge clk);
     if(busy || cycles!==N*N*N/LANES) $fatal(1,"completion cycles");
     for(i=0;i<N;i=i+1) begin
       for(j=0;j<N;j=j+1) begin
         expected=0;
         for(k=0;k<N;k=k+1) expected=expected+av[i*N+k]*bv[k*N+j];
         address=i*N+j; #1;
         if(data_out!==expected) $fatal(1,"arithmetic row %0d col %0d expected %0d got %0d",i,j,expected,data_out);
       end
     end
     address=16'hffff; #1;
     if(data_out!==0) $fatal(1,"out-of-range read");
     repeat(3) @(negedge clk);
     if(!done || busy || cycles!==N*N*N/LANES) $fatal(1,"sticky completion");
   end
 endtask
 initial begin
   repeat(3) @(negedge clk);
   reset=0;
   if(busy || done || cycles!==0) $fatal(1,"reset protocol");
   load_operands(0);
   launch;
   // A write and another start during execution must both be ignored.
   load=1; operand_b=0; address=0; data_in=127; start=1;
   @(negedge clk); load=0; start=0;
   check_result;
   // Same operands are reusable; accumulators and cycle counter must clear.
   launch;
   check_result;
   load_operands(1);
   launch;
   repeat(7) @(negedge clk);
   reset=1; @(negedge clk); reset=0;
   if(busy || done || cycles!==0) $fatal(1,"reset abort");
   // Reset invalidates completion; reload inputs and prove recovery.
   load_operands(1);
   launch;
   check_result;
   $display("PASS lifecycle N=%0d LANES=%0d",N,LANES);
   $finish;
 end
 initial begin #1000000; $fatal(1,"timeout"); end
endmodule
