# Read-only KV260 presence check for run_board.py --check (MATMUL-BOARD-001).
# Lists the JTAG chain only: no reset, no boot-mode change, no programming,
# no memory reads or writes. Prints "CHECK ..." lines for run_board.py to parse.
if {[catch {connect} e]} {
  puts "CHECK ERROR connect failed: [string map {"\n" " | "} $e]"
  puts "CHECK END"
  exit
}
set serial ""
catch {
  foreach t [targets -target-properties] {
    if {[dict exists $t jtag_cable_serial] && [dict get $t jtag_cable_serial] ne ""} {
      set serial [dict get $t jtag_cable_serial]; break
    }
  }
}
puts "CHECK CABLE $serial"
if {[catch {jtag targets} chain]} {
  puts "CHECK ERROR jtag targets failed: [string map {"\n" " | "} $chain]"
} else {
  foreach line [split $chain "\n"] {
    set s [string trim $line]
    if {$s ne ""} { puts "CHECK DEVICE $s" }
  }
}
catch {disconnect}
puts "CHECK END"
