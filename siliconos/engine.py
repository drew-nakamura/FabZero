import hashlib
import json
import random
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = dict(operation="matrix_multiply", size=8, precision="int8", target="kv260",
               frequency_mhz=100, max_dsps=16, max_lanes=4, objective="minimize_latency")

def validate(spec):
    if not isinstance(spec, dict):
        raise ValueError("Specification must be an object.")
    if set(spec) - set(DEFAULT):
        raise ValueError("Unknown specification fields: " + ", ".join(set(spec)-set(DEFAULT)))
    result = {**DEFAULT, **spec}
    for key in ("size", "frequency_mhz", "max_dsps", "max_lanes"):
        if type(result[key]) is not int:
            raise ValueError(key + " must be an integer.")
    if result["operation"] != "matrix_multiply" or result["precision"] != "int8" or result["target"] != "kv260":
        raise ValueError("Currently supported: INT8 matrix multiplication targeting KV260 only.")
    if result["size"] not in (8,16) or result["max_lanes"] not in (1,4):
        raise ValueError("Supported sizes are 8/16; lane limits are 1/4.")
    if not 1 <= result["frequency_mhz"] <= 200 or not 0 <= result["max_dsps"] <= 1248:
        raise ValueError("Clock must be 1–200 MHz; DSP budget must be 0–1248.")
    if result["objective"] not in ("minimize_latency", "minimize_lanes"):
        raise ValueError("Unsupported objective. Power optimization needs physical measurements.")
    return result

def explore(spec):
    spec = validate(spec)
    n = spec["size"]
    candidates = []
    for lanes in (1,4):
        cycles = n**3 // lanes
        candidates.append(dict(id=f"mac{lanes}", lanes=lanes, cycles=cycles,
            projected_us=cycles/spec["frequency_mhz"], gops=2*lanes*spec["frequency_mhz"]/1000,
            within_lane_limit=lanes<=spec["max_lanes"], evidence="analytical",
            dsp=None, lut=None, bram=None, timing_closed=False, dsp_budget_verified=False))
    allowed = [c for c in candidates if c["within_lane_limit"]]
    key = "cycles" if spec["objective"] == "minimize_latency" else "lanes"
    provisional = min(allowed, key=lambda c:c[key])["id"]
    return dict(spec=spec,candidates=candidates,provisional=provisional,hardware_recommendation=None,
        warning="DSP budget and clock feasibility are unverified until Vivado implementation. Lane count is not DSP count.")

def reference(a,b,n):
    return [sum(a[i*n+k]*b[k*n+j] for k in range(n)) for i in range(n) for j in range(n)]

def simulate(spec, lanes, seed=42, vectors=None):
    spec=validate(spec)
    if type(lanes) is not int or lanes not in (1,4) or lanes>spec["max_lanes"]:
        raise ValueError("Candidate exceeds the lane limit or is unsupported.")
    if type(seed) is not int or not 0<=seed<=2**31-1:
        raise ValueError("Seed must be an integer between 0 and 2147483647.")
    if not shutil.which("iverilog") or not shutil.which("vvp"):
        raise ValueError("Icarus Verilog is unavailable. Install iverilog to run RTL simulation.")
    n=spec["size"]; rng=random.Random(seed)
    a,b=vectors or ([rng.randrange(-128,128) for _ in range(n*n)], [rng.randrange(-128,128) for _ in range(n*n)])
    expected=reference(a,b,n)
    source_bytes={name:(ROOT/"hardware"/name).read_bytes() for name in ("matmul.sv","tb.sv")}
    sources={name:hashlib.sha256(content).hexdigest() for name,content in source_bytes.items()}
    with tempfile.TemporaryDirectory(prefix="siliconos-") as td:
        path=Path(td)
        (path/"inputs.hex").write_text("\n".join(f"{x&255:02x}" for x in a+b)+"\n")
        for name,content in source_bytes.items():
            (path/name).write_bytes(content)
        command=["iverilog","-g2012","-s","tb",f"-Ptb.N={n}",f"-Ptb.LANES={lanes}","-o",str(path/"sim"),"matmul.sv","tb.sv"]
        begin=time.monotonic()
        subprocess.run(command,cwd=td,check=True,capture_output=True,timeout=20)
        run=subprocess.run(["vvp",str(path/"sim")],cwd=td,check=True,capture_output=True,text=True,timeout=20)
        wall=time.monotonic()-begin
    outputs=[int(line.split()[1]) for line in run.stdout.splitlines() if line.startswith("OUT ")]
    cycles=[int(line.split()[1]) for line in run.stdout.splitlines() if line.startswith("CYCLES ")]
    if outputs != expected or len(cycles)!=1:
        raise ValueError("RTL correctness failed. No performance result accepted.")
    version=subprocess.run(["iverilog","-V"],capture_output=True,text=True,timeout=5).stdout.splitlines()[0]
    return dict(evidence="rtl_simulation",correct=True,spec=spec,lanes=lanes,seed=seed,cycles=cycles[0],
        projected_us=cycles[0]/spec["frequency_mhz"],clock_status="assumed target; not measured",physical_fpga=False,
        simulator=version,simulator_wall_seconds=wall,source_sha256=sources,
        simulator_stdout=run.stdout,parameters={"N":n,"LANES":lanes},
        source_files={name:content.decode("utf-8") for name,content in source_bytes.items()},
        input_sha256=hashlib.sha256(bytes(x&255 for x in a+b)).hexdigest(),
        output_sha256=hashlib.sha256(json.dumps(outputs).encode()).hexdigest(),
        inputs={"a":a,"b":b},outputs=outputs,operations=2*n**3,
        resources={"dsp":None,"lut":None,"bram":None},
        limitations=["Generic AXI wrapper is simulated separately; board integration and deployment are pending.","Local operand arrays are not validated BRAM banking.","Parallel speedup spends more arithmetic capacity; no fixed-resource optimization claim.","Input loading, host transfer, and deployment are excluded from kernel cycles."])
