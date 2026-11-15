# Load bring-up bitstream over JTAG and read PL results (BRINGUP-001).
# Usage (from hw/bringup): xsdb run_pl_probe.tcl
# Boot-mode change is volatile: a power cycle returns the board to factory QSPI boot.
# No QSPI/SD writes are performed.
set here [file normalize [file dirname [info script]]]
source $here/build/addresses.tcl
connect
puts "TARGETS (before):\n[targets]"
targets -set -nocase -filter {name =~ "*PSU*"}
mwr 0xff5e0200 0x0100   ;# CRL_APB.BOOT_MODE_USER: use alternate boot mode = JTAG
rst -system
after 2000
targets -set -nocase -filter {name =~ "*APU*"}
source $here/build/psu_init.tcl
psu_init
after 500
fpga -file $here/build/bringup.bit
after 500
psu_ps_pl_isolation_removal
after 200
psu_ps_pl_reset_config
targets -set -nocase -filter {name =~ "*A53*#0"}
rst -processor
after 200
# xsdb blocks PL AXI addresses until they are declared (flags 3 = read+write).
memmap -addr $GPIO0 -size 0x10000 -flags 3
memmap -addr $GPIO1 -size 0x10000 -flags 3
puts "TARGETS (after):\n[targets]"
proc rd {a} { return [lindex [mrd -value $a 1] 0] }
set id [rd [expr {$GPIO1 + 8}]]
puts [format "BUILD_ID   = 0x%08X (expect 0xFAB00001)" $id]
set c1 [rd $GPIO1]; after 100; set c2 [rd $GPIO1]
puts [format "COUNT      = 0x%08X then 0x%08X (delta %d)" $c1 $c2 [expr {($c2 - $c1) & 0xFFFFFFFF}]]
set fails 0
if {$id != 0xFAB00001} { incr fails }
if {$c1 == $c2} { incr fails }
foreach x {0 1 7 0x12345678 0xFFFFFFFF} {
  mwr $GPIO0 $x
  set y [rd [expr {$GPIO0 + 8}]]
  set exp [expr {(3*$x + 1) & 0xFFFFFFFF}]
  set ok [expr {$y == $exp ? "PASS" : "FAIL"}]
  if {$ok eq "FAIL"} { incr fails }
  puts [format "x=0x%08X y=0x%08X expect=0x%08X %s" $x $y $exp $ok]
}
puts [expr {$fails == 0 ? "PL_PROBE_RESULT: PASS" : "PL_PROBE_RESULT: FAIL ($fails)"}]
