# xsdb board script for matmul_axi on the KV260 (MATMUL-BOARD-001).
# Do not run directly: run_board.py verifies the artifact hashes, writes the
# inputs file, starts this script, and judges every value it prints.
#
#   xsdb run_matmul.tcl BIT PSU_INIT ADDRESSES INPUTS N
#
# BIT        bitstream already hash-checked by run_board.py
# PSU_INIT   psu_init.tcl from the same build
# ADDRESSES  addresses.tcl from the same build (sets MATMUL_BASE, MATMUL_RANGE)
# INPUTS     Tcl file setting A and B (N*N signed INT8 each, row-major)
# N          matrix size
#
# Prints only raw readings as "MM ..." lines; it makes no pass/fail decision.
# Boot-mode change is volatile (a power cycle restores factory QSPI boot).
# No QSPI/SD/eMMC writes. Same JTAG sequence as hw/bringup/run_pl_probe.tcl.
if {[llength $argv] != 5} { error "usage: run_matmul.tcl BIT PSU_INIT ADDRESSES INPUTS N" }
lassign $argv BIT PSU_INIT ADDRESSES INPUTS N
source $ADDRESSES
source $INPUTS
set NN [expr {$N * $N}]
set POLL_LIMIT 2000        ;# each JTAG read is ~ms; the kernel finishes in microseconds

proc now_ns {} { return [expr {[clock microseconds] * 1000}] }
proc rd {off} { return [lindex [mrd -value [expr {$::MATMUL_BASE + $off}] 1] 0] }
proc wr {off v} { mwr [expr {$::MATMUL_BASE + $off}] [expr {$v & 0xFFFFFFFF}] }
proc s32 {v} { return [expr {$v >= 0x80000000 ? $v - 0x100000000 : $v}] }

proc load_operands {} {
  for {set i 0} {$i < $::NN} {incr i} {
    wr 0x0c $i
    wr 0x10 [expr {[lindex $::A $i] & 0xFF}]
  }
  for {set i 0} {$i < $::NN} {incr i} {
    wr 0x0c [expr {0x10000 | $i}]
    wr 0x10 [expr {[lindex $::B $i] & 0xFF}]
  }
}

# Start, poll with a finite limit, read all outputs and both cycle halves.
proc run_job {label t0} {
  wr 0x04 1
  set polls 0
  set s [rd 0x08]
  while {($s & 3) != 2 && $polls < $::POLL_LIMIT} { incr polls; set s [rd 0x08] }
  if {($s & 3) != 2} {
    puts "MM JOB $label status=$s polls=$polls timeout=1"
    return
  }
  set outs {}
  for {set i 0} {$i < $::NN} {incr i} {
    wr 0x0c $i
    lappend outs [s32 [rd 0x14]]
  }
  set lo [rd 0x18]
  set hi [rd 0x1c]
  set dt [expr {[now_ns] - $t0}]
  puts "MM JOB $label status=$s polls=$polls timeout=0 cycles_lo=$lo cycles_hi=$hi host_ns=$dt"
  puts "MM OUT $label [join $outs { }]"
}

proc main {} {
  connect
  set serial unknown
  catch {
    foreach t [targets -target-properties] {
      if {[dict exists $t jtag_cable_serial] && [dict get $t jtag_cable_serial] ne ""} {
        set serial [dict get $t jtag_cable_serial]; break
      }
    }
  }
  puts "MM CABLE $serial"
  targets -set -nocase -filter {name =~ "*PSU*"}
  mwr 0xff5e0200 0x0100   ;# CRL_APB.BOOT_MODE_USER: alternate boot mode = JTAG (volatile)
  rst -system
  after 2000
  targets -set -nocase -filter {name =~ "*APU*"}
  # Global scope: psu_init.tcl keeps its register tables in global variables.
  uplevel #0 [list source $::PSU_INIT]
  psu_init
  after 500
  set t0 [now_ns]
  fpga -file $::BIT
  puts "MM PROGRAM_NS [expr {[now_ns] - $t0}]"
  after 500
  psu_ps_pl_isolation_removal
  after 200
  psu_ps_pl_reset_config
  targets -set -nocase -filter {name =~ "*A53*#0"}
  rst -processor
  after 200
  # xsdb blocks PL AXI addresses until declared (flags 3 = read+write).
  memmap -addr $::MATMUL_BASE -size $::MATMUL_RANGE -flags 3

  # Interface check before any job.
  set id [rd 0x00]; set n [rd 0x20]; set l [rd 0x24]; set s [rd 0x08]
  puts "MM ID $id"
  puts "MM N $n"
  puts "MM LANES $l"
  puts "MM STATUS_IDLE $s"
  if {$id != 0x53494c01 || $n != $::N || ($s & 1)} {
    puts "MM ABORT interface check failed; no job started"
    return
  }
  wr 0x0c 5; set r5 [rd 0x0c]; wr 0x0c 0; set r0 [rd 0x0c]
  puts "MM SCRATCH $r5 $r0"

  set t0 [now_ns]
  load_operands
  run_job first $t0
  run_job repeat [now_ns]            ;# same operands, no reload

  # PL reset pulse (pl_resetn0 via psu_init's EMIO sequence), then reload and rerun.
  targets -set -nocase -filter {name =~ "*APU*"}
  psu_ps_pl_reset_config
  targets -set -nocase -filter {name =~ "*A53*#0"}
  after 100
  puts "MM RESET status=[rd 0x08] cycles_lo=[rd 0x18] cycles_hi=[rd 0x1c]"
  set t0 [now_ns]
  load_operands
  run_job reset_reload $t0
}

puts "MM BEGIN n=$N base=$MATMUL_BASE"
if {[catch {main} err]} { puts "MM ERROR [string map {"\n" " | "} $err]" }
catch {disconnect}
puts "MM END"
