// Board bring-up top level (BRINGUP-001): PS block design + pl_probe.
// No package pins are used, so no pin constraints are required.
module bringup_top;
  localparam logic [31:0] BUILD_ID = 32'hFAB0_0001;

  logic        clk, rst_n;
  logic [31:0] x, y, count;

  bringup_bd_wrapper u_bd (
    .pl_clk0  (clk),
    .pl_rst_n (rst_n),
    .x_out    (x),
    .y_in     (y),
    .count_in (count),
    .id_in    (BUILD_ID)
  );

  pl_probe u_probe (
    .clk   (clk),
    .rst_n (rst_n),
    .x     (x),
    .y     (y),
    .count (count)
  );
endmodule
