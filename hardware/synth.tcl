# Kernel or AXI slave out-of-context synthesis. Not a board design or bitstream flow.
# vivado -mode batch -source hardware/synth.tcl -tclargs PART N LANES INPUT_BITS PERIOD_NS OUT_DIR ?TOP?
if {$argc != 6 && $argc != 7} {
    error "Usage: synth.tcl PART N LANES INPUT_BITS PERIOD_NS OUT_DIR ?TOP? (explicit installed part required)"
}
lassign $argv part n lanes input_bits period outdir top
if {$top eq ""} { set top matmul }
if {$top ni {matmul matmul_axi}} { error "TOP must be matmul or matmul_axi" }
if {$n ni {8 16} || $lanes ni {1 2 4} || $input_bits ni {2 4 8}} { error "Supported N: 8/16; LANES: 1/2/4; INPUT_BITS: 2/4/8" }
if {![string is double -strict $period] || $period <= 0} { error "PERIOD_NS must be positive" }
if {[llength [get_parts -quiet $part]] != 1} { error "Select exactly one installed Vivado PART: $part" }
set source_dir [file dirname [file normalize [info script]]]
file mkdir $outdir
set outdir [file normalize $outdir]
read_verilog -sv [file join $source_dir matmul.sv]
if {$top eq "matmul_axi"} { read_verilog -sv [file join $source_dir matmul_axi.sv] }
synth_design -top $top -part $part -mode out_of_context -generic [list N=$n LANES=$lanes INPUT_BITS=$input_bits]
set clock_port [expr {$top eq "matmul_axi" ? "aclk" : "clk"}]
create_clock -name kernel_clk -period $period [get_ports $clock_port]
report_utilization -file [file join $outdir utilization_synth.rpt]
report_timing_summary -report_unconstrained -file [file join $outdir timing_synth.rpt]
report_drc -file [file join $outdir drc_synth.rpt]
write_checkpoint -force [file join $outdir matmul_synth.dcp]
set manifest [open [file join $outdir build_metadata.txt] w]
puts $manifest "evidence=out_of_context_synthesis"
puts $manifest "vivado=[version -short]"
puts $manifest "top=$top\npart=$part\nN=$n\nLANES=$lanes\nINPUT_BITS=$input_bits\nrequested_period_ns=$period"
puts $manifest "source=[file join $source_dir matmul.sv]"
if {$top eq "matmul_axi"} { puts $manifest "wrapper_source=[file join $source_dir matmul_axi.sv]" }
puts $manifest "physical_fpga=false\ntiming_closed=false"
puts $manifest "Post-synthesis estimates only. No place/route, board wrapper, I/O timing contract, or bitstream."
close $manifest
