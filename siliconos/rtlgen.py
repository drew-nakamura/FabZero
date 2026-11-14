"""Conservative, tool-free gate for generated matmul source.

This intentionally accepts a small synthesizable subset, not arbitrary SystemVerilog.
It checks syntax boundaries and interface shape; simulation proves tested arithmetic.
It is not an OS sandbox for hostile compiler inputs.
"""
import re

MAX_SOURCE_BYTES = 65536
# Trusted second simulation root. The checked-in tb.sv stays byte-for-byte intact.
# Observe actual execution clocks instead of trusting a candidate's cycle register.
CYCLE_MONITOR = '''`timescale 1ns/1ps
module rtl_monitor;
 reg [63:0] counted=0;
 reg active=0, completed=0;
 always @(posedge tb.clk) begin
   if(tb.reset) begin
     counted=0; active=0; completed=0;
     #1;
     if(tb.busy!==0 || tb.done!==0 || tb.cycles!==0) $fatal(1,"generated RTL reset protocol failed");
   end else if(tb.start && !tb.busy) begin
     if(active) $fatal(1,"generated RTL dropped busy before completion");
     counted=0; active=1; completed=0;
     #1;
     if(tb.busy!==1 || tb.done!==0 || tb.cycles!==0) $fatal(1,"generated RTL start protocol failed");
   end else if(active) begin
     if(tb.busy!==1) $fatal(1,"generated RTL busy protocol failed");
     counted=counted+1;
     #1;
     if(tb.cycles!==counted) $fatal(1,"generated RTL cycle counter disagrees with observed clocks");
     if(tb.done===1) begin
       if(tb.busy!==0) $fatal(1,"generated RTL completion protocol failed");
       active=0; completed=1;
     end else if(tb.done!==0 || tb.busy!==1) $fatal(1,"generated RTL execution protocol failed");
   end else begin
     #1;
     if(tb.busy!==0 || tb.done!==completed || tb.cycles!==counted)
       $fatal(1,"generated RTL idle protocol failed");
   end
 end
endmodule
'''
PORTS = {
    'clk': ('input', False, None), 'reset': ('input', False, None),
    'start': ('input', False, None), 'load': ('input', False, None),
    'operand_b': ('input', False, None), 'address': ('input', False, '15:0'),
    'data_in': ('input', True, '7:0'), 'busy': ('output', False, None),
    'done': ('output', False, None), 'cycles': ('output', False, '63:0'),
    'data_out': ('output', True, '31:0'),
}


def _reject(detail):
    raise ValueError('Generated RTL rejected before tool execution: ' + detail)


def gate(source):
    """Return the exact original text on success; never repair/strip candidate code."""
    if not isinstance(source, str) or not source.strip():
        _reject('expected nonempty raw SystemVerilog.')
    if len(source.encode('utf-8')) > MAX_SOURCE_BYTES:
        _reject('source exceeds the 64 KiB limit.')
    if any(ord(c) > 126 or (ord(c) < 32 and c not in '\n\r\t') for c in source):
        _reject('only ASCII source text is supported.')
    # Lex comments before tokens, so strings cannot hide directives or extra modules.
    code = []
    i = 0
    while i < len(source):
        if source.startswith('//', i):
            end = source.find('\n', i)
            i = len(source) if end < 0 else end
            code.append(' ')
        elif source.startswith('/*', i):
            end = source.find('*/', i + 2)
            if end < 0: _reject('unterminated comment.')
            i = end + 2
            code.append(' ')
        elif source[i] in '`"\\':
            _reject('directives, strings and escaped identifiers are forbidden.')
        else:
            code.append(source[i])
            i += 1
    code = ''.join(code)
    if re.search(r'\(\*|\*\)', code.replace('@(*)', '@*')):
        _reject('attributes are forbidden.')
    if re.search(r'\b(?:initial|final|task|endtask|function|endfunction|import|export|'
                 r'package|endpackage|interface|endinterface|program|endprogram|'
                 r'primitive|endprimitive|bind|force|release|defparam|specify|endspecify|'
                 r'fork|join|join_any|join_none|wait|disable|forever|while|repeat|'
                 r'event|time|realtime|real|shortreal|timeunit|timeprecision|'
                 r'alias|class|endclass|virtual|extern|rand|randc|assert|assume|cover)\b', code):
        _reject('unsupported procedural or external construct.')
    for token in re.findall(r'\$[A-Za-z0-9_$]*', code):
        if token not in ('$signed', '$unsigned', '$clog2'):
            _reject('system tasks/functions other than $signed/$unsigned/$clog2 are forbidden.')
    # Dot is never needed in this subset: reject hierarchy, method calls and real literals.
    if '.' in code:
        _reject('hierarchical references and real literals are forbidden.')
    match = re.fullmatch(r'\s*module\s+matmul\s*#\s*\(([^()]*)\)\s*\(([^()]*)\)\s*;'
                         r'(.*?)\bendmodule\s*', code, re.S)
    if not match or len(re.findall(r'\b(?:module|endmodule)\b', code)) != 2:
        _reject('expected exactly one ANSI module matmul with N/LANES parameters.')
    parameters, ports, body = match.groups()
    found = {}
    for item in parameters.split(','):
        parameter = re.fullmatch(r'\s*parameter\s+(?:(?:integer|int)\s+)?'
                                 r'(N|LANES)\s*=\s*(\d+)\s*', item)
        if not parameter or parameter[1] in found:
            _reject('parameters must be exactly N and LANES with literal defaults.')
        found[parameter[1]] = int(parameter[2])
    if set(found) != {'N', 'LANES'} or found['N'] not in (8, 16) or found['LANES'] not in (1, 4):
        _reject('supported parameter defaults are N=8/16 and LANES=1/4.')
    declared = {}
    declaration = None
    for item in ports.split(','):
        port = re.fullmatch(r'\s*(?:(input|output)\s+(?:(?:wire|reg|logic)\s+)?'
                           r'(?:(signed|unsigned)\s+)?(?:\[\s*(\d+\s*:\s*\d+)\s*\]\s*)?)?'
                           r'([A-Za-z_][A-Za-z0-9_]*)\s*', item)
        if not port or port[4] in declared:
            _reject('invalid or duplicate port declaration.')
        if port[1]:
            declaration = (port[1], port[2] == 'signed', re.sub(r'\s', '', port[3]) if port[3] else None)
        if declaration is None: _reject('ports require ANSI directions and widths.')
        declared[port[4]] = declaration
    if declared != PORTS:
        _reject('ports must exactly match tb.sv names, directions, signedness and widths.')
    if '#' in body:
        _reject('delays and parameterized instances are forbidden.')
    # Only ordinary clock/combinational sensitivities; no event controls inside blocks.
    body_without_controls = re.sub(
        r'\balways\s*@\s*(?:\(\s*posedge\s+clk\s*\)|\(\s*\*\s*\)|\*)', 'always', body)
    if '@' in body_without_controls:
        _reject('only always @(posedge clk), always @* or always_comb are supported.')
    for call in re.findall(r'([A-Za-z_$][A-Za-z0-9_$]*)\s*\(', body_without_controls):
        if call not in ('if', 'for', 'case', 'casez', 'casex', '$signed', '$unsigned', '$clog2'):
            _reject('module instances and user-defined calls are forbidden.')
    if re.search(r'\]\s*\(', body_without_controls):
        _reject('instance arrays are forbidden.')
    return source
