"""KV260 stage of the live pipeline: Vivado build evidence, board check, and board runs.

The app calls the same tools as hw/matmul_board/DEMO_RUNBOOK.md:
run_board.py --check, run_board.py --handoff, then sign_result.py's file checks
and HMAC signing. The signed result is imported through server.import_board_result,
which re-checks it against the simulation run. One board job runs at a time.
"""
import hashlib
import io
import json
import re
import subprocess
import sys
import threading
import time
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from . import board, handoff

ROOT = Path(__file__).resolve().parents[1]
HW = ROOT / "hw" / "matmul_board"
BUILD = HW / "build"
RESULTS = HW / "results"
HANDOFFS = RESULTS / ".app"  # ZIPs written for app-started board runs (git-ignored)
RESULT_FOLDER = re.compile(r"\d{8}T\d{6}Z_n8_l[14](?:-\d+)?")
RESULT_FILES = {"xsdb.log": "text/plain; charset=utf-8", "board-result.json": "application/json"}
BOARD_RUN_TIMEOUT_S = 900  # run_board.py's own xsdb timeout is 600 s

JOBS = {}
_JOBS_LOCK = threading.Lock()


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _now():
    return datetime.now(timezone.utc).isoformat()


# ------------------------------------------------------------------ Vivado evidence
def _build_dir(lanes):
    if lanes not in (1, 4):
        raise ValueError("LANES must be 1 or 4.")
    return BUILD / f"n8_l{lanes}"


def build_evidence(lanes):
    """The committed Vivado build for N=8/LANES, with every file re-hashed now."""
    bd = _build_dir(lanes)
    m = json.loads((bd / "implementation_manifest.json").read_text(encoding="utf-8"))
    s = json.loads((bd / "summary" / "summary.json").read_text(encoding="utf-8"))["summaries"][0]
    app_rtl = {name: _sha(ROOT / "hardware" / name) for name in ("matmul.sv", "matmul_axi.sv")}
    started, finished = (datetime.fromisoformat(m[k]) for k in ("build_started_at", "created_at"))
    t, p, syn = s["timing"], s["power"], s.get("synthesis") or {}
    fmax = next((f["estimated_fmax_mhz"] for f in t.get("fmax_estimates", []) if f["clock"] == "clk_pl_0"), None)
    worst = (t.get("kernel_worst_paths") or [None])[0]
    return {
        "lanes": lanes, "N": 8,
        "vivado": m["vivado_version"], "part": m["target_part"], "board_part": m["board_part"],
        "build_started_at": m["build_started_at"], "build_finished_at": m["created_at"],
        "build_minutes": round((finished - started).total_seconds() / 60, 1),
        "rtl_sha256": m["rtl"]["sha256"],
        "rtl_matches_app": all(m["rtl"]["sha256"].get(k) == v for k, v in app_rtl.items()),
        "bitstream": f"matmul_board_n8_l{lanes}.bit",
        "bitstream_sha256": m["bitstream_sha256"],
        "bitstream_verified": _sha(bd / f"matmul_board_n8_l{lanes}.bit") == m["bitstream_sha256"],
        "summary_verified": _sha(bd / "summary" / "summary.json") == m["artifacts_sha256"]["summary.json"],
        "configured_clock_hz": m["configured_clock_hz"],
        "timing": {"met": bool(m["timing"]["timing_met"]), "WNS_ns": t["WNS"], "WHS_ns": t["WHS"],
                   "WPWS_ns": t["WPWS"], "endpoints": t["TNS_endpoints"],
                   "failing": t["TNS_failing"] + t["THS_failing"] + t["TPWS_failing"],
                   "constraint_mhz": 100.0, "fmax_estimate_mhz": fmax,
                   "kernel_worst_path": worst and {k: worst.get(k) for k in (
                       "slack_ns", "source", "destination", "data_path_delay_ns", "logic_levels", "logic_detail")}},
        "area": s["area"], "area_scope": s["area_scope"],
        "power": {k: p.get(k) for k in ("total_w", "dynamic_w", "static_w", "kernel_w", "junction_c", "confidence")},
        "drc_clean": m["drc_clean"], "drc_by_severity": m.get("drc_by_severity") or {},
        "methodology_by_severity": m.get("methodology_by_severity") or {},
        "synthesis": {"errors": syn.get("errors"), "critical_warnings": syn.get("critical_warnings"),
                      "rtl_components": syn.get("rtl_components") or []},
        "reports": [{"name": name, "sha256": want, "verified": _sha(bd / "reports" / name) == want}
                    for name, want in sorted(m["report_sha256"].items())],
        "address_map": m["address_map"],
        "limitations": m.get("limitations") or [],
    }


def report_text(lanes, name):
    """One Vivado report, only if it is listed in the manifest and its hash still matches."""
    bd = _build_dir(lanes)
    m = json.loads((bd / "implementation_manifest.json").read_text(encoding="utf-8"))
    want = (m.get("report_sha256") or {}).get(name)
    if not want:
        raise LookupError("Report not found")
    path = bd / "reports" / name
    if _sha(path) != want:
        raise ValueError("Report file no longer matches the implementation manifest.")
    return path.read_bytes()


def result_file(folder, name):
    """A file from one board run folder (raw JTAG transcript or runner result)."""
    if not RESULT_FOLDER.fullmatch(folder or "") or name not in RESULT_FILES:
        raise LookupError("Result not found")
    path = RESULTS / folder / name
    if not path.is_file():
        raise LookupError("Result not found")
    return path.read_bytes(), RESULT_FILES[name]


def find_result_folder(runner_result_id):
    """The results/ folder holding this runner_result_id (for runs imported before the folder was recorded)."""
    for path in sorted(RESULTS.glob("*/board-result.json"), reverse=True):
        if RESULT_FOLDER.fullmatch(path.parent.name):
            try:
                if json.loads(path.read_text(encoding="utf-8")).get("runner_result_id") == runner_result_id:
                    return path.parent.name
            except (OSError, ValueError):
                continue
    return None


def handoff_contents(run):
    """What the FPGA handoff ZIP for this run contains (per-file SHA256 from its manifest)."""
    body = handoff.archive(run)
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        manifest = json.loads(z.read("manifest.json"))
        sizes = {i.filename: i.file_size for i in z.infolist()}
    files = [{"name": name, "sha256": digest, "bytes": sizes.get(name)}
             for name, digest in sorted(manifest["files_sha256"].items())]
    files.append({"name": "manifest.json", "sha256": None, "bytes": sizes.get("manifest.json")})
    return {"run_id": run["id"], "parameters": manifest["parameters"], "source_evidence": manifest["source_evidence"],
            "files": files}


# ------------------------------------------------------------------ board check
def check_board(check_file):
    """Read-only JTAG check through run_board.py --check (no programming)."""
    try:
        p = subprocess.run([sys.executable, "-u", str(HW / "run_board.py"), "--check"], capture_output=True,
                           text=True, timeout=180, cwd=ROOT)
        output = (p.stdout + p.stderr).strip()
    except subprocess.TimeoutExpired:
        output = "board check timed out after 180 s"
    status = board.board_status(check_file)
    try:
        rec = json.loads(Path(check_file).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        rec = {}
    return {**status, "devices": rec.get("devices") or [], "output": output[-2000:]}


# ------------------------------------------------------------------ board runs
def _public(job):
    out = {k: v for k, v in job.items() if not k.startswith("_")}
    if job["status"] == "running":
        out["elapsed_s"] = round(time.monotonic() - job["_t0"], 1)
    out["log"] = list(job["log"][-40:])
    return out


def get_job(job_id):
    with _JOBS_LOCK:
        job = JOBS.get(job_id)
        return _public(job) if job else None


def start_board_run(run, import_result):
    """Start an asynchronous board run for a verified 8x8 simulation run of the checked-in RTL."""
    spec = run.get("spec") or {}
    if run.get("evidence") != "rtl_simulation" or run.get("correct") is not True:
        raise ValueError("Only a verified simulation of the checked-in RTL can run on the KV260 "
                         "(AI-generated RTL has no bitstream).")
    if spec.get("target") != "kv260" or spec.get("size") != 8 or run.get("lanes") not in (1, 4):
        raise ValueError("The KV260 bitstreams are built for 8x8 with 1 or 4 lanes only.")
    with _JOBS_LOCK:
        if any(j["status"] == "running" for j in JOBS.values()):
            raise ValueError("A board run is already active. Wait for it to finish.")
        job = {"id": str(uuid.uuid4()), "parent_run_id": run["id"], "lanes": run["lanes"], "status": "running",
               "stage": "export", "message": "Writing the FPGA handoff ZIP", "started_at": _now(),
               "_t0": time.monotonic(), "log": [], "error": None,
               "zip_sha256": None, "result_folder": None, "child_id": None}
        JOBS[job["id"]] = job
    threading.Thread(target=_board_run, args=(job, run, import_result), daemon=True).start()
    return _public(job)


def _stage(job, stage, message):
    with _JOBS_LOCK:
        job.update(stage=stage, message=message)
        job["log"].append(f"[{stage}] {message}")


def _board_run(job, run, import_result):
    try:
        HANDOFFS.mkdir(parents=True, exist_ok=True)
        zpath = HANDOFFS / f"siliconos-{run['id']}-handoff.zip"
        body = handoff.archive(run)
        zpath.write_bytes(body)
        with _JOBS_LOCK:
            job["zip_sha256"] = hashlib.sha256(body).hexdigest()
        _stage(job, "board", "Checking the ZIP against the bitstream, programming the FPGA and running the job")
        proc = subprocess.Popen([sys.executable, "-u", str(HW / "run_board.py"), "--handoff", str(zpath)],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=ROOT)
        lines = []
        for line in proc.stdout:
            line = line.rstrip()
            lines.append(line)
            with _JOBS_LOCK:
                job["log"].append(line[:500])
        code = proc.wait(timeout=BOARD_RUN_TIMEOUT_S)
        verdict = next((l for l in reversed(lines) if l.startswith("MATMUL_BOARD_RESULT:")), None)
        found = verdict and re.search(r"[\\/](" + RESULT_FOLDER.pattern + r")\s*$", verdict)
        if found:
            with _JOBS_LOCK:
                job["result_folder"] = found.group(1)
        if code != 0 or not verdict or not verdict.startswith("MATMUL_BOARD_RESULT: PASS") or not found:
            raise RuntimeError((verdict or (lines[-1] if lines else "run_board.py produced no output"))
                               .replace("MATMUL_BOARD_RESULT: ", "Board run "))
        _stage(job, "sign", "Re-hashing the bitstream and Vivado reports, then signing the result (HMAC-SHA256)")
        if str(HW) not in sys.path:
            sys.path.insert(0, str(HW))
        import sign_result  # hw/matmul_board/sign_result.py: same checks as the command-line signer
        envelope = board.sign(sign_result.build_payload(RESULTS / job["result_folder"]))
        _stage(job, "import", "Checking the signed result against the simulation run and saving it")
        child = import_result(run["id"], envelope)
        with _JOBS_LOCK:
            job.update(status="done", stage="done", child_id=child["id"],
                       message=f"Imported board run {child['id'][:8]}: {child['cycles']} cycles, "
                               f"{len(child['outputs'])} outputs verified")
    except Exception as e:  # report every failure on the job; never a silent pass
        with _JOBS_LOCK:
            job.update(status="failed", error=str(e) or e.__class__.__name__, message="Failed")
    finally:
        with _JOBS_LOCK:
            job["elapsed_s"] = round(time.monotonic() - job["_t0"], 1)
