"""Portable, provenance-checked FPGA handoff from an accepted run."""
import hashlib
import io
import json
import zipfile
from .engine import ROOT, validate, reference


def archive(report):
    spec=validate(report.get('spec'))
    if report.get('correct') is not True or report.get('evidence') not in ('rtl_simulation','ai_generated_rtl','generic_synthesis'):
        raise ValueError('A verified simulation or synthesis run is required.')
    lanes=report.get('lanes')
    if type(lanes) is not int or lanes not in (1,2,4) or lanes>spec['max_lanes']:
        raise ValueError('Invalid run lane configuration.')
    files={}
    sources=report.get('source_files',{}); hashes=report.get('source_sha256',{})
    generated = report.get('evidence') == 'ai_generated_rtl' or report.get('source_origin') == 'ai_generated_rtl'
    required = ('matmul.sv','tb.sv','rtl_monitor.sv') if generated else ('matmul.sv','tb.sv')
    for name in required:
        source=sources.get(name)
        if not isinstance(source,str) or hashlib.sha256(source.encode()).hexdigest()!=hashes.get(name):
            raise ValueError('Run source snapshot is missing or its hash does not match.')
        files['hardware/'+name]=source
    n=spec['size']; bits=int(spec['precision'][3:]); inputs=report.get('inputs',{})
    a,b=inputs.get('a'),inputs.get('b')
    low, high=-(1 << (bits-1)), 1 << (bits-1)
    if any(not isinstance(v,list) or len(v)!=n*n or any(type(x) is not int or not low<=x<high for x in v) for v in (a,b)):
        raise ValueError('Run inputs are invalid.')
    if report.get('outputs')!=reference(a,b,n):
        raise ValueError('Run outputs do not match the independent reference.')
    files['inputs.hex']='\n'.join(f'{x&255:02x}' for x in a+b)+'\n'
    files['expected.json']=json.dumps({'inputs':inputs,'outputs':report['outputs'],'cycles':report.get('cycles'),'parameters':{'N':n,'LANES':lanes,'INPUT_BITS':bits}},indent=2)
    # These are current integration aids, not historical evidence for this run.
    for name in ('matmul_axi.sv','synth.tcl','BRINGUP.md'):
        files['integration/'+name]=(ROOT/'hardware'/name).read_text()
    files['integration/matmul.sv']=sources['matmul.sv']
    period=1000/spec['frequency_mhz']
    monitor_flags=' -s rtl_monitor' if generated else ''
    monitor_file=' hardware/rtl_monitor.sv' if generated else ''
    files['README.md']=f'''# Verified kernel handoff

Board reported: AMD SK-KV260-G. Windows 11, Vivado/Vitis 2025.2.
Run: {report.get('id','unsaved')}; evidence: {report['evidence']}.
N={n}, LANES={lanes}, INPUT_BITS={bits} ({spec['precision'].upper()}); clock period {period:g} ns is a target, not achieved timing.

From this archive root, replay the exact RTL with Icarus:

    iverilog -g2012 -s tb{monitor_flags} -Ptb.N={n} -Ptb.LANES={lanes} -Ptb.INPUT_BITS={bits} -o replay hardware/matmul.sv hardware/tb.sv{monitor_file}
    vvp replay

Compare printed OUT values to expected.json. This replay is not a board run.
Generated RTL archives include the original independent cycle monitor in this replay.

In the Vivado Tcl shell, inspect `version -short`, `get_board_parts *kv260*`,
and `get_parts *xck26*`. Select the exact installed part matching the board.
From a Windows command prompt with Vivado on PATH:

    vivado -mode batch -source integration/synth.tcl -tclargs EXACT_INSTALLED_PART {n} {lanes} {bits} {period:g} build/ooc

That produces out-of-context synthesis only, not a deployable bitstream.
The integration/ files are current aids, separately hashed in manifest.json;
the wrapper has not been verified against this exact archived kernel on a board.
See integration/BRINGUP.md. Confirm PS block design, reset/clock, MMIO address,
OS/firmware and compatible loader before deployment. No physical address is assumed.
For an ASIC-origin run this is a proposed FPGA retarget, not FPGA validation.
'''
    files['manifest.json']=json.dumps({'schema_version':1,'run_id':report.get('id'),
        'source_evidence':report['evidence'],'original_target':spec['target'],
        'requested_target':'kv260','board_sku':'SK-KV260-G','reported_vivado':'2025.2',
        'parameters':{'N':n,'LANES':lanes,'INPUT_BITS':bits},'physical_fpga':False,
        'integration_status':'unverified for this run',
        'files_sha256':{name:hashlib.sha256(value.encode()).hexdigest() for name,value in files.items()}},indent=2)
    output=io.BytesIO()
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as bundle:
        for name,value in files.items():bundle.writestr(name,value)
    return output.getvalue()
