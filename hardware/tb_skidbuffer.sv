module tb;
reg clk=0; always #5 clk=~clk;
reg reset=1,valid=0,ready=0;
reg [7:0] data=0;
wire in_ready,out_valid;
wire [7:0] out_data;
skidbuffer #(.DW(8),.OPT_OUTREG(1),.OPT_LOWPOWER(0),.OPT_PASSTHROUGH(0),.OPT_INITIAL(0)) dut
(.i_clk(clk),.i_reset(reset),.i_valid(valid),.o_ready(in_ready),.i_data(data),.o_valid(out_valid),.i_ready(ready),.o_data(out_data));
integer sent=0,received=0,step=0,epoch=0;
reg stalled=0; reg [7:0] held;
initial begin
 for(epoch=0;epoch<2;epoch=epoch+1) begin
  @(negedge clk); reset=1; valid=0; ready=0;
  repeat(2) @(negedge clk);
  if(out_valid) $fatal(1,"reset did not flush valid");
  reset=0; sent=0; received=0; stalled=0;
  for(step=0;step<600;step=step+1) begin
   valid=(sent<200); data=sent; ready=(step%7>2);
   @(posedge clk);
   if(stalled && (!out_valid || out_data!==held)) $fatal(1,"unstable stalled output");
   if(valid && in_ready) sent=sent+1;
   if(out_valid && ready) begin
    if(received>=sent || out_data!==(received & 255)) $fatal(1,"lost/reordered data");
    received=received+1;
   end
   stalled=out_valid&&!ready; held=out_data;
   @(negedge clk);
  end
  if(sent!=200 || received!=200) $fatal(1,"incomplete transfer");
  // Queue data under backpressure, then reset at the next epoch.
  valid=1; data=77; ready=0; repeat(3) @(negedge clk);
 end
 $display("PASS skidbuffer: stalls, ordering, drain, reset and restart"); $finish;
end
endmodule
