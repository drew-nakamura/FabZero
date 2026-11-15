# Write a consistent set of Vivado reports for hw/tools/vivado_summary.py.
#
# Usage:
#   vivado -mode batch -source hw/tools/collect_reports.tcl -tclargs INPUT OUT_DIR ?KERNEL_INSTANCE?
#
# INPUT is a design checkpoint (.dcp) or a project (.xpr). For a project, the
# implemented run (impl_1) is opened when complete, otherwise synth_1.
# KERNEL_INSTANCE (optional) is the hierarchical instance name of the block to
# highlight, e.g. u_mm or u_bd/bringup_bd_i/matmul_0. Its worst paths are
# written to kernel_paths.rpt.
#
# Power from this script uses Vivado's default vectorless activity estimates.
if {$argc < 2 || $argc > 3} {
  error "Usage: collect_reports.tcl INPUT OUT_DIR ?KERNEL_INSTANCE?"
}
lassign $argv input outdir kernel
set input [file normalize $input]
file mkdir $outdir
set outdir [file normalize $outdir]

set ext [string tolower [file extension $input]]
if {$ext eq ".dcp"} {
  open_checkpoint $input
  set opened "checkpoint $input"
} elseif {$ext eq ".xpr"} {
  open_project $input
  if {[get_property PROGRESS [get_runs impl_1]] eq "100%"} {
    open_run impl_1
    set opened "project $input run impl_1"
  } elseif {[get_property PROGRESS [get_runs synth_1]] eq "100%"} {
    open_run synth_1
    set opened "project $input run synth_1"
  } else {
    error "Neither impl_1 nor synth_1 has completed in $input"
  }
} else {
  error "INPUT must be a .dcp or .xpr file: $input"
}

report_utilization -file $outdir/utilization.rpt
report_utilization -hierarchical -hierarchical_depth 8 -file $outdir/utilization_hier.rpt
report_timing_summary -max_paths 10 -report_unconstrained -file $outdir/timing_summary.rpt
report_power -hierarchical_depth 8 -file $outdir/power.rpt
report_drc -file $outdir/drc.rpt
report_methodology -file $outdir/methodology.rpt

if {$kernel ne ""} {
  set kcells [get_cells -quiet -hierarchical -filter "NAME == $kernel"]
  if {[llength $kcells] != 1} {
    error "KERNEL_INSTANCE '$kernel' matched [llength $kcells] cells; give the full hierarchical name"
  }
  set kregs [get_cells -quiet -hierarchical -filter "NAME =~ $kernel/* && IS_SEQUENTIAL"]
  if {[llength $kregs] > 0} {
    # Data inputs only, so reset/enable paths do not hide the kernel's real logic paths.
    set kd [get_pins -quiet -of_objects $kregs -filter {REF_PIN_NAME == D}]
    if {[llength $kd] == 0} { set kd $kregs }
    report_timing -max_paths 5 -nworst 1 -to $kd -file $outdir/kernel_paths.rpt
  }
}

set fh [open $outdir/design_info.txt w]
puts $fh "vivado=[version -short]"
puts $fh "opened=$opened"
puts $fh "top=[get_property TOP [current_design]]"
puts $fh "part=[get_property PART [current_design]]"
puts $fh "kernel_instance=$kernel"
puts $fh "collected_at=[clock format [clock seconds] -format {%Y-%m-%dT%H:%M:%S%z}]"
close $fh
puts "COLLECT_DONE $outdir"
