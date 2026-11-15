// KV260 board top (MATMUL-BOARD-001): PS block design + teammate matmul_axi.
// The block design exports one AXI4-Lite master (M_AXI, 32-bit data, 32-bit
// address carrying base+offset; one 4 KB segment), the ~100 MHz PL clock it
// runs on, and its synchronized active-low peripheral reset (proc_sys_reset).
// matmul_axi decodes only address bits 7:0, so within the 4 KB segment the
// 256-byte register map repeats every 0x100 bytes; the host uses base+0x00..0x24.
// N and LANES are set by the build script (build.tcl -> generic on this top).
// No package pins are used, so no pin constraints are required.
module matmul_board_top #(parameter int N = 8, parameter int LANES = 1);
  logic        clk, rst_n;
  logic [31:0] awaddr, araddr;
  logic        awvalid, awready, wvalid, wready, bvalid, bready;
  logic        arvalid, arready, rvalid, rready;
  logic [31:0] wdata, rdata;
  logic [3:0]  wstrb;
  logic [1:0]  bresp, rresp;

  matmul_board_bd_wrapper u_bd (
    .pl_clk0       (clk),
    .pl_rst_n      (rst_n),
    .M_AXI_awaddr  (awaddr),
    .M_AXI_awvalid (awvalid),
    .M_AXI_awready (awready),
    .M_AXI_wdata   (wdata),
    .M_AXI_wstrb   (wstrb),
    .M_AXI_wvalid  (wvalid),
    .M_AXI_wready  (wready),
    .M_AXI_bresp   (bresp),
    .M_AXI_bvalid  (bvalid),
    .M_AXI_bready  (bready),
    .M_AXI_araddr  (araddr),
    .M_AXI_arvalid (arvalid),
    .M_AXI_arready (arready),
    .M_AXI_rdata   (rdata),
    .M_AXI_rresp   (rresp),
    .M_AXI_rvalid  (rvalid),
    .M_AXI_rready  (rready)
  );

  matmul_axi #(.N(N), .LANES(LANES)) u_matmul (
    .aclk          (clk),
    .aresetn       (rst_n),
    .s_axi_awaddr  (awaddr[7:0]),
    .s_axi_awvalid (awvalid),
    .s_axi_awready (awready),
    .s_axi_wdata   (wdata),
    .s_axi_wstrb   (wstrb),
    .s_axi_wvalid  (wvalid),
    .s_axi_wready  (wready),
    .s_axi_bresp   (bresp),
    .s_axi_bvalid  (bvalid),
    .s_axi_bready  (bready),
    .s_axi_araddr  (araddr[7:0]),
    .s_axi_arvalid (arvalid),
    .s_axi_arready (arready),
    .s_axi_rdata   (rdata),
    .s_axi_rresp   (rresp),
    .s_axi_rvalid  (rvalid),
    .s_axi_rready  (rready)
  );
endmodule
