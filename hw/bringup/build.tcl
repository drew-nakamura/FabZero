# Reproducible KV260 bring-up build (BRINGUP-001).
# Usage (from hw/bringup): vivado -mode batch -source build.tcl
set here  [file normalize [file dirname [info script]]]
set out   $here/build
file mkdir $out
create_project bringup $out/proj -part xck26-sfvc784-2LV-c -force
set_property board_part xilinx.com:kv260_som:part0:1.4 [current_project]

create_bd_design bringup_bd
set ps [create_bd_cell -type ip -vlnv xilinx.com:ip:zynq_ultra_ps_e zynq_ultra_ps_e_0]
apply_bd_automation -rule xilinx.com:bd_rule:zynq_ultra_ps_e \
  -config {apply_board_preset "1"} $ps
# One AXI master (HPM0_FPD) only, so no unused master clocks dangle.
set_property -dict [list CONFIG.PSU__USE__M_AXI_GP0 {1} CONFIG.PSU__USE__M_AXI_GP1 {0} \
  CONFIG.PSU__USE__M_AXI_GP2 {0}] $ps

set g0 [create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio axi_gpio_0]
set_property -dict [list CONFIG.C_IS_DUAL {1} CONFIG.C_ALL_OUTPUTS {1} CONFIG.C_GPIO_WIDTH {32} \
  CONFIG.C_ALL_INPUTS_2 {1} CONFIG.C_GPIO2_WIDTH {32}] $g0
set g1 [create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio axi_gpio_1]
set_property -dict [list CONFIG.C_IS_DUAL {1} CONFIG.C_ALL_INPUTS {1} CONFIG.C_GPIO_WIDTH {32} \
  CONFIG.C_ALL_INPUTS_2 {1} CONFIG.C_GPIO2_WIDTH {32}] $g1

foreach g {axi_gpio_0 axi_gpio_1} {
  apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config [list \
    Master /zynq_ultra_ps_e_0/M_AXI_HPM0_FPD Clk_master Auto Clk_slave Auto Clk_xbar Auto \
    Slave /$g/S_AXI intc_ip Auto ddr_seg Auto master_apm 0] [get_bd_intf_pins $g/S_AXI]
}

create_bd_port -dir O -type clk pl_clk0
connect_bd_net [get_bd_pins zynq_ultra_ps_e_0/pl_clk0] [get_bd_ports pl_clk0]
set rst [get_bd_cells -filter {VLNV =~ "*proc_sys_reset*"}]
create_bd_port -dir O -type rst pl_rst_n
connect_bd_net [get_bd_pins $rst/peripheral_aresetn] [get_bd_ports pl_rst_n]
foreach {name dir pin} {x_out O axi_gpio_0/gpio_io_o  y_in I axi_gpio_0/gpio2_io_i
                        count_in I axi_gpio_1/gpio_io_i id_in I axi_gpio_1/gpio2_io_i} {
  create_bd_port -dir $dir -from 31 -to 0 $name
  connect_bd_net [get_bd_pins $pin] [get_bd_ports $name]
}
assign_bd_address
validate_bd_design
save_bd_design

# Record the actual assigned addresses for the xsdb test script.
set fh [open $out/addresses.tcl w]
foreach seg [get_bd_addr_segs -of_objects [get_bd_addr_spaces zynq_ultra_ps_e_0/Data]] {
  if {[string match *axi_gpio_0* $seg]} { puts $fh "set GPIO0 [get_property OFFSET $seg]" }
  if {[string match *axi_gpio_1* $seg]} { puts $fh "set GPIO1 [get_property OFFSET $seg]" }
}
close $fh

make_wrapper -files [get_files bringup_bd.bd] -top
add_files -norecurse [glob $out/proj/bringup.gen/sources_1/bd/bringup_bd/hdl/bringup_bd_wrapper.v]
add_files -norecurse [list $here/pl_probe.sv $here/bringup_top.sv]
set_property top bringup_top [current_fileset]
update_compile_order -fileset sources_1

launch_runs synth_1 -jobs 4
wait_on_run synth_1
if {[get_property PROGRESS [get_runs synth_1]] ne "100%"} { error "synthesis failed" }
launch_runs impl_1 -to_step write_bitstream -jobs 4
wait_on_run impl_1
if {[get_property PROGRESS [get_runs impl_1]] ne "100%"} { error "implementation/bitstream failed" }

open_run impl_1
report_timing_summary -file $out/timing_summary.rpt
report_drc -file $out/drc.rpt
report_utilization -file $out/utilization.rpt
file copy -force [glob $out/proj/bringup.runs/impl_1/bringup_top.bit] $out/bringup.bit
file copy -force [glob $out/proj/bringup.gen/sources_1/bd/bringup_bd/ip/*zynq_ultra_ps_e_0*/psu_init.tcl] $out/psu_init.tcl
write_hw_platform -fixed -include_bit -force $out/bringup.xsa
puts "WNS=[get_property STATS.WNS [get_runs impl_1]] WHS=[get_property STATS.WHS [get_runs impl_1]]"
puts "BUILD_DONE"
