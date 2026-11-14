// Board bring-up diagnostic only (BRINGUP-001). Not customer/product logic.
// y = 3*x + 1 (registered) proves input-dependent PL computation;
// count is a free-running counter on pl_clk0 proving the PL is clocked.
module pl_probe (
  input  logic        clk,
  input  logic        rst_n,
  input  logic [31:0] x,
  output logic [31:0] y,
  output logic [31:0] count
);
  always_ff @(posedge clk) begin
    if (!rst_n) begin
      y     <= '0;
      count <= '0;
    end else begin
      y     <= (x << 1) + x + 32'd1;
      count <= count + 32'd1;
    end
  end
endmodule
