# OFFLINE TEST HARNESS ONLY (no hardware): runs the real run_matmul.tcl inside
# xsdb with the JTAG commands replaced by a behavioral model of matmul_axi's
# register map. Used by test_run_board.py to check the script's sequencing and
# output format. Output from this harness is never board evidence.
#
#   xsdb mock_board.tcl FAULT LANES BIT PSU_INIT ADDRESSES INPUTS N
#
# FAULT: none | result | cycles | hang | identity | noreset | lanes
lassign $argv FAULT MLANES
set argv [lrange $argv 2 end]
set MN [lindex $argv 4]
set ::mock [dict create addr 0 operand 0 busy 0 done 0 cycles 0]
array set ::mA {}; array set ::mB {}; array set ::mC {}
source [lindex $argv 2]   ;# addresses.tcl for MATMUL_BASE

proc s8 {v} { set v [expr {$v & 0xFF}]; return [expr {$v >= 128 ? $v - 256 : $v}] }
proc mock_compute {} {
  global MN MLANES FAULT
  for {set r 0} {$r < $MN} {incr r} {
    for {set c 0} {$c < $MN} {incr c} {
      set acc 0
      for {set k 0} {$k < $MN} {incr k} {
        set acc [expr {$acc + [s8 $::mA([expr {$r*$MN+$k}])] * [s8 $::mB([expr {$k*$MN+$c}])]}]
      }
      set ::mC([expr {$r*$MN+$c}]) [expr {$acc & 0xFFFFFFFF}]
    }
  }
  if {$FAULT eq "result"} { set ::mC(5) [expr {($::mC(5) + 1) & 0xFFFFFFFF}] }
  set cyc [expr {$MN*$MN*$MN/$MLANES}]
  if {$FAULT eq "cycles"} { incr cyc }
  dict set ::mock cycles $cyc
  if {$FAULT eq "hang"} { dict set ::mock busy 1; return }
  dict set ::mock done 1
}
proc mock_reset {} {
  if {$::FAULT ne "noreset"} { dict set ::mock done 0; dict set ::mock cycles 0 }
  dict set ::mock busy 0; dict set ::mock addr 0; dict set ::mock operand 0
}
proc mock_read {a} {
  set off [expr {$a - $::MATMUL_BASE}]
  if {$off < 0 || $off >= 0x1000} { return 0 }
  set m $::mock
  switch -- [expr {$off & 0xFF}] {
    0   { return [expr {$::FAULT eq "identity" ? 0 : 0x53494c01}] }
    8   { return [expr {[dict get $m busy] | ([dict get $m done] && ![dict get $m busy]) << 1}] }
    12  { return [dict get $m addr] }
    16  { return [dict get $m operand] }
    20  {
      if {![dict get $m done] || [dict get $m busy]} { error "Memory read error at $a (mock SLVERR)" }
      set i [expr {[dict get $m addr] & 0xFFFF}]
      return [expr {[info exists ::mC($i)] ? $::mC($i) : 0}]
    }
    24  { return [expr {[dict get $m cycles] & 0xFFFFFFFF}] }
    28  { return [expr {[dict get $m cycles] >> 32}] }
    32  { return $::MN }
    36  { return [expr {$::FAULT eq "lanes" ? 3 : $::MLANES}] }
    default { error "Memory read error at $a (mock SLVERR)" }
  }
}
proc mock_write {a v} {
  set off [expr {$a - $::MATMUL_BASE}]
  if {$off < 0 || $off >= 0x1000} { return }
  switch -- [expr {$off & 0xFF}] {
    4  { if {$v & 1} { mock_compute } }
    12 { dict set ::mock addr $v }
    16 {
      set ad [dict get $::mock addr]; set i [expr {$ad & 0xFFFF}]
      dict set ::mock operand [expr {$v & 0xFF}]
      if {$ad & 0x10000} { set ::mB($i) $v } else { set ::mA($i) $v }
    }
  }
}
# Replace the hardware-touching xsdb commands.
proc connect {args} {}
proc disconnect {args} {}
proc targets {args} { if {"-target-properties" in $args} { return [list [dict create jtag_cable_serial MOCK0000]] } }
proc rst {args} {}
proc fpga {args} {}
proc memmap {args} {}
proc mrd {args} { return [list [mock_read [lindex $args end-1]]] }
proc mwr {args} { mock_write [lindex $args end-1] [lindex $args end] }

source [file join [file dirname [file dirname [file normalize [info script]]]] run_matmul.tcl]
