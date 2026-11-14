import unittest
from siliconos.engine import ROOT
from siliconos.rtlgen import gate, MAX_SOURCE_BYTES

SOURCE = (ROOT / 'hardware/matmul.sv').read_text()


class StaticGateTests(unittest.TestCase):
    def test_accepts_exact_source_and_logic_variants_without_mutation(self):
        for source in (SOURCE, SOURCE.replace('wire', 'logic').replace('reg ', 'logic '),
                       SOURCE.replace('parameter N=8', 'parameter integer N=16'),
                       '// $system `include module evil;\n' + SOURCE,
                       SOURCE.replace('a[row*N+k]', '$signed(a[row*N+k])')):
            self.assertEqual(gate(source), source)

    def test_rejects_contract_changes(self):
        changes = [('module matmul', 'module other'), ('parameter N=8', 'parameter N=32'),
                   ('parameter LANES=1', 'parameter EXTRA=1'),
                   ('input wire clk', 'input wire signed clk'), ('reset, start', 'start'),
                   ('[15:0] address', '[14:0] address'), ('signed [7:0]', '[7:0]'),
                   ('output reg busy', 'input reg busy'), ('busy, done', 'busy, busy'),
                   ('clk, reset', 'clk, extra, reset')]
        for before, after in changes:
            with self.subTest(after=after), self.assertRaisesRegex(ValueError, 'before tool execution'):
                gate(SOURCE.replace(before, after))

    def test_rejects_untrusted_constructs_and_extra_design_units(self):
        snippets = ['$system("whoami");', '$readmemh("inputs.hex", a);', '$display("OUT 0");',
                    '$finish;', '$random;', '$fopen;', '$dumpoff;', '`include "tb.sv"',
                    'assign c[0] = tb.inputs[0];', 'force done=1;', 'initial begin end',
                    'final begin end', 'function f; endfunction', 'task f; endtask',
                    'wire \\escaped ;', '(* blackbox *) wire x;', 'bind tb x y();',
                    'helper instance_name();', 'and (busy, clk, reset);', 'matmul m[2]();',
                    'always #1 busy=0;', 'always @(negedge clk) busy=0;',
                    'always @(posedge clk) begin @(posedge clk); end',
                    '/* unterminated', '"/*" $system("x");']
        for snippet in snippets:
            with self.subTest(snippet=snippet), self.assertRaises(ValueError):
                gate(SOURCE.replace('endmodule', snippet + '\nendmodule'))
        for source in (None, '', '```verilog\n' + SOURCE + '```', SOURCE + '\nmodule tb; endmodule',
                       SOURCE + 'package p; endpackage', SOURCE + '\x00', SOURCE + '//é',
                       SOURCE + ' ' * MAX_SOURCE_BYTES):
            with self.assertRaises(ValueError): gate(source)
