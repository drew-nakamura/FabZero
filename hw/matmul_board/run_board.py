#!/usr/bin/env python3
"""Fixed board runner for matmul_axi on the KV260 over JTAG (MATMUL-BOARD-001).

Live run (board plugged in, J4 USB + J12 power, no SD card):
  python hw/matmul_board/run_board.py --lanes 1
  python hw/matmul_board/run_board.py --lanes 4
Offline check of the result writer against a saved transcript (no board):
  python hw/matmul_board/run_board.py --lanes 1 --replay TRANSCRIPT --results-dir DIR

Writes hw/matmul_board/results/<run_id>/{board-result.json, inputs.json, xsdb.log}
per docs/spec/BOARD_RESULT_FILE.md (temporary folder, renamed when complete;
failed runs are written too, with status "fail"). Prints one line:
  MATMUL_BOARD_RESULT: PASS|FAIL (...) <run folder>

Safety (emailed spec section 11): only the allowlisted build folder
build/n<N>_l<LANES>/ is accepted; its implementation manifest must report
timing met and DRC clean; the bitstream hash must match the manifest before
loading; identity/N/LANES are checked before results are trusted; JTAG work has
a finite timeout. No arbitrary paths, commands or addresses are accepted.
xsdb only reports readings; every pass/fail decision is made here, against an
independent Python reference model.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
XSDB = Path(r"C:/AMDDesignTools/2025.2/Vivado/bin/xsdb.bat")
IDENTITY = 0x53494C01
XSDB_TIMEOUT_S = 600
LIVE_RESULTS = HERE / "results"


# ------------------------------------------------------------- reference model
def reference_matmul(a, b, n):
    """Independent oracle: signed INT8 x INT8, INT32 accumulation, row-major."""
    c = []
    for r in range(n):
        for col in range(n):
            acc = sum(a[r * n + k] * b[k * n + col] for k in range(n))
            c.append(((acc + 2**31) % 2**32) - 2**31)
    return c


def identity_ramp(n):
    a = [1 if r == col else 0 for r in range(n) for col in range(n)]
    b = [i - 32 for i in range(n * n)]
    return a, b


def mismatches(actual, expected):
    if not isinstance(actual, list) or len(actual) != len(expected):
        return [("length", len(actual) if isinstance(actual, list) else None, len(expected))]
    return [(i, x, y) for i, (x, y) in enumerate(zip(actual, expected)) if x != y]


def comparator_self_check(expected):
    """Prove the comparison can fail: identical values must match, and a
    deliberately wrong expectation (one element off by one) must not."""
    wrong = list(expected)
    wrong[0] = wrong[0] + 1
    return not mismatches(list(expected), expected) and len(mismatches(wrong, expected)) == 1


def canon_sha(obj):
    return hashlib.sha256(json.dumps(obj, separators=(",", ":")).encode("utf-8")).hexdigest()


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ------------------------------------------------------------- transcript parse
def parse_transcript(text):
    t = {"lines": [], "jobs": {}, "outs": {}, "errors": [], "aborts": []}
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("MM "):
            continue
        t["lines"].append(line)
        try:
            parse_line(t, line)
        except (ValueError, IndexError) as e:
            t["errors"].append(f"unparseable line {line[:80]!r}: {e}")
    return t


def parse_line(t, line):
    parts = line.split()
    tag = parts[1] if len(parts) > 1 else ""
    rest = parts[2:]
    if tag in ("BEGIN", "END"):
        t[tag.lower()] = True
    elif tag == "ERROR":
        t["errors"].append(" ".join(rest))
    elif tag == "ABORT":
        t["aborts"].append(" ".join(rest))
    elif tag == "CABLE":
        t["cable"] = rest[0] if rest else None
    elif tag in ("PROGRAM_NS", "ID", "N", "LANES", "STATUS_IDLE"):
        t[tag.lower()] = int(rest[0])
    elif tag == "SCRATCH":
        t["scratch"] = [int(rest[0]), int(rest[1])]
    elif tag == "JOB":
        t["jobs"][rest[0]] = {k: int(v) for k, v in (kv.split("=") for kv in rest[1:])}
    elif tag == "OUT":
        t["outs"][rest[0]] = [int(v) for v in rest[1:]]
    elif tag == "RESET":
        t["reset"] = {k: int(v) for k, v in (kv.split("=") for kv in rest)}


def job_result(t, label, expected, want_cycles):
    """Return (ok, details, reasons) for one job."""
    j = t["jobs"].get(label)
    outs = t["outs"].get(label)
    if j is None:
        return False, {"outputs_match": False, "cycles": None}, [f"{label}: job missing"]
    reasons = []
    if j.get("timeout"):
        reasons.append(f"{label}: done timeout (status {j.get('status')} after {j.get('polls')} polls)")
    elif (j.get("status", 0) & 3) != 2:
        reasons.append(f"{label}: final status {j.get('status')} is not done-idle")
    cycles = None
    if "cycles_lo" in j and "cycles_hi" in j:
        cycles = (j["cycles_hi"] << 32) | j["cycles_lo"]
    match = outs is not None and not mismatches(outs, expected)
    if not match:
        bad = mismatches(outs, expected) if outs is not None else [("missing",)]
        reasons.append(f"{label}: {len(bad)} output mismatch(es), first {bad[0]}")
    if cycles != want_cycles:
        reasons.append(f"{label}: cycles {cycles} != expected {want_cycles}")
    return not reasons, {"outputs_match": match, "cycles": cycles}, reasons


# ------------------------------------------------------------- result building
def build_result(t, manifest, manifest_sha, a, b, n, lanes, workload_id, evidence_on_pass, extra_reasons):
    expected = reference_matmul(a, b, n)
    want_cycles = n ** 3 // lanes
    reasons = list(extra_reasons)
    if not t.get("begin") or not t.get("end"):
        reasons.append("transcript incomplete (missing MM BEGIN/END)")
    reasons += [f"xsdb error: {e}" for e in t["errors"]]
    reasons += [f"xsdb abort: {e}" for e in t["aborts"]]
    if t.get("id") != IDENTITY:
        reasons.append(f"identity {t.get('id')} != {IDENTITY}")
    if t.get("n") != n:
        reasons.append(f"compiled N {t.get('n')} != {n}")
    if t.get("lanes") != lanes:
        reasons.append(f"compiled LANES {t.get('lanes')} != {lanes}")
    if t.get("status_idle") is None or (t["status_idle"] & 1):
        reasons.append(f"status before first job {t.get('status_idle')} is not idle")
    scratch_ok = t.get("scratch") == [5, 0]
    if not scratch_ok:
        reasons.append(f"address register scratch test read {t.get('scratch')}, expected [5, 0]")

    ok1, first, r1 = job_result(t, "first", expected, want_cycles)
    ok2, rep, r2 = job_result(t, "repeat", expected, want_cycles)
    ok3, rr, r3 = job_result(t, "reset_reload", expected, want_cycles)
    reasons += r1 + r2 + r3
    reset = t.get("reset")
    if reset is None:
        reasons.append("reset check missing")
    else:
        if reset.get("status") != 0:
            reasons.append(f"status after PL reset {reset.get('status')} != 0 (done not cleared)")
        if reset.get("cycles_lo") != 0 or reset.get("cycles_hi") != 0:
            reasons.append(f"cycle counter after PL reset not zero: {reset}")
    outputs = t["outs"].get("first", [])
    if not comparator_self_check(expected):
        reasons.append("comparator self-check failed: a deliberately wrong expectation did not mismatch")
    if not manifest.get("timing", {}).get("timing_met") or not manifest.get("drc_clean"):
        reasons.append("implementation manifest does not report timing met and DRC clean")

    status = "pass" if not reasons else "fail"
    b_ = manifest
    return {
        "schema_version": 1,
        "runner_result_id": str(uuid.uuid4()),
        "parent_run_id": None,
        "status": status,
        "failure_reason": "; ".join(reasons) if reasons else None,
        # Spec section 11: never claim board_measured when any required check fails.
        "evidence": evidence_on_pass if status == "pass" else None,
        "recorded_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "workload_id": workload_id,
        "source_sha256": b_["rtl"]["sha256"],
        "build": {
            "bitstream_sha256": b_["bitstream_sha256"],
            "vivado_version": b_["vivado_version"],
            "target_part": b_["target_part"],
            "board_part": b_["board_part"],
            "top": b_["logical_top"],
            "board_top": b_["board_top"],
            "parameters": {"N": b_["parameters"]["N"], "LANES": b_["parameters"]["LANES"]},
            "configured_clock_hz": b_["configured_clock_hz"],
            "timing_met": bool(b_["timing"]["timing_met"]),
            "implementation_manifest_sha256": manifest_sha,
        },
        "board": {
            "sku": "SK-KV260-G",
            "board_revision": None,
            "image_identity": "none: JTAG boot, no operating system",
            "kernel_version": None,
            "firmware_identity": "QSPI U-Boot 2023.01 (May 10 2024); bypassed by JTAG boot",
            "loader": "xsdb 2025.2 over JTAG (hw_server 2025.2)",
            "jtag_cable_serial": t.get("cable"),
        },
        "interface_check": {
            "base_address": b_["address_map"]["base_address"],
            "identity": t.get("id"),
            "compiled_n": t.get("n"),
            "compiled_lanes": t.get("lanes"),
            "scratch_register_ok": scratch_ok,
        },
        "run": {
            "input_sha256": canon_sha({"A": a, "B": b}),
            "outputs": outputs,
            "output_sha256": canon_sha(outputs),
            "expected_outputs_match": first["outputs_match"],
            "cycles": first["cycles"],
            "kernel_timing_boundary": "accelerator busy clocks",
            "host_elapsed_ns": t["jobs"].get("first", {}).get("host_ns"),
            "programming_elapsed_ns": t.get("program_ns"),
        },
        "repeat_checks": {
            "repeat_without_reload": {
                "outputs_match": rep["outputs_match"] and t["outs"].get("repeat") == outputs,
                "cycles": rep["cycles"]},
            "reset_reload_rerun": {
                "outputs_match": rr["outputs_match"] and t["outs"].get("reset_reload") == outputs,
                "cycles": rr["cycles"]},
        },
    }


def run_xsdb(bit, bdir, A, B, n, extra):
    """Run run_matmul.tcl on the board with a finite timeout; return the raw transcript."""
    # xsdb starts hw_server, which keeps running after xsdb exits and inherits the
    # working directory; so run from the build folder (not the temp folder, which
    # Windows could then not delete) and tolerate cleanup errors.
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
        inp = Path(td) / "inputs.tcl"
        inp.write_text(f"set A {{{' '.join(map(str, A))}}}\nset B {{{' '.join(map(str, B))}}}\n")
        cmd = [str(XSDB), str(HERE / "run_matmul.tcl"), bit.as_posix(),
               (bdir / "psu_init.tcl").as_posix(), (bdir / "addresses.tcl").as_posix(),
               inp.as_posix(), str(n)]
        print("> " + " ".join(cmd), flush=True)
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=XSDB_TIMEOUT_S, cwd=bdir)
            if p.returncode != 0:
                extra.append(f"xsdb exit code {p.returncode}")
            return p.stdout + ("\n--- stderr ---\n" + p.stderr if p.stderr else "")
        except subprocess.TimeoutExpired as e:
            out = e.stdout.decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
            extra.append(f"xsdb timeout after {XSDB_TIMEOUT_S} s")
            return out + f"\n--- runner: xsdb killed after {XSDB_TIMEOUT_S} s timeout ---\n"


def load_inputs(path, n):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    a, b = data.get("A"), data.get("B")
    for name, v in (("A", a), ("B", b)):
        if not (isinstance(v, list) and len(v) == n * n and
                all(isinstance(x, int) and not isinstance(x, bool) and -128 <= x <= 127 for x in v)):
            sys.exit(f"inputs: {name} must be {n * n} integers in [-128, 127]")
    return a, b


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=8, choices=[8])
    ap.add_argument("--lanes", type=int, required=True, choices=[1, 4])
    ap.add_argument("--inputs", help="JSON {\"A\": [...], \"B\": [...]} signed INT8 row-major "
                                     "(default: identity A, B[i] = i - 32)")
    ap.add_argument("--workload-id", help="label for --inputs (default identity-ramp-v1)")
    ap.add_argument("--build-dir", help=argparse.SUPPRESS)  # tests only; must be under build/
    ap.add_argument("--replay", help="offline: parse this saved xsdb transcript instead of using the board")
    ap.add_argument("--results-dir", help="replay only: output folder (never the live results folder)")
    a = ap.parse_args(argv)

    n, lanes = a.n, a.lanes
    tag = f"n{n}_l{lanes}"
    bdir = Path(a.build_dir).resolve() if a.build_dir else HERE / "build" / tag
    if a.build_dir and not a.replay:
        sys.exit("--build-dir is only allowed with --replay")
    mpath = bdir / "implementation_manifest.json"
    if not mpath.exists():
        sys.exit(f"no implementation manifest at {mpath}; build first (build.py --lanes {lanes})")
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    manifest_sha = file_sha(mpath)
    if manifest["parameters"] != {"N": n, "LANES": lanes}:
        sys.exit(f"manifest parameters {manifest['parameters']} do not match N={n} LANES={lanes}")

    if a.inputs:
        A, B = load_inputs(a.inputs, n)
        workload = a.workload_id or "custom-" + canon_sha({"A": A, "B": B})[:12]
    else:
        A, B = identity_ramp(n)
        workload = "identity-ramp-v1"

    extra = []
    if a.replay:
        if not a.results_dir:
            sys.exit("--replay needs --results-dir")
        results = Path(a.results_dir).resolve()
        if results == LIVE_RESULTS.resolve() or LIVE_RESULTS.resolve() in results.parents:
            sys.exit("replay output must not go into the live results folder")
        transcript = Path(a.replay).read_text(encoding="utf-8", errors="replace")
        evidence = "replay_test_not_board"
        run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"_{tag}_replay"
    else:
        results = LIVE_RESULTS
        evidence = "board_measured"
        run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"_{tag}"
        bit = bdir / f"matmul_board_{tag}.bit"
        if not (manifest["timing"]["timing_met"] and manifest["drc_clean"]):
            sys.exit("refusing to load: manifest does not report timing met and DRC clean")
        if file_sha(bit) != manifest["bitstream_sha256"]:
            sys.exit("refusing to load: bitstream hash does not match the implementation manifest")
        for name in ("psu_init.tcl", "addresses.tcl"):
            if file_sha(bdir / name) != manifest["artifacts_sha256"][name]:
                sys.exit(f"refusing to load: {name} hash does not match the implementation manifest")
        # One active board job at a time (spec section 11).
        results.mkdir(parents=True, exist_ok=True)
        lock = results / ".runner.lock"
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            sys.exit(f"another board run holds {lock}; if no run is active (e.g. after a crash), delete it")
        try:
            os.write(fd, f"pid {os.getpid()} {run_id}\n".encode())
            os.close(fd)
            transcript = run_xsdb(bit, bdir, A, B, n, extra)
        finally:
            lock.unlink(missing_ok=True)

    try:
        t = parse_transcript(transcript)
        result = build_result(t, manifest, manifest_sha, A, B, n, lanes, workload, evidence, extra)
    except Exception as e:  # never lose a board transcript: write a failed run instead
        result = {"schema_version": 1, "runner_result_id": str(uuid.uuid4()), "parent_run_id": None,
                  "status": "fail", "failure_reason": f"runner error while judging: {e!r}",
                  "evidence": None, "recorded_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
                  "workload_id": workload}

    results.mkdir(parents=True, exist_ok=True)
    # Never overwrite an existing run folder: add -2, -3, ... if the name is taken.
    base_id, k = run_id, 1
    while (results / run_id).exists() or (results / f".tmp_{run_id}").exists():
        k += 1
        run_id = f"{base_id}-{k}"
    final = results / run_id
    tmp = results / f".tmp_{run_id}"
    tmp.mkdir()
    (tmp / "inputs.json").write_text(json.dumps({"A": A, "B": B}, separators=(",", ":")), encoding="utf-8")
    (tmp / "xsdb.log").write_text(transcript, encoding="utf-8")
    (tmp / "board-result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, final)
    verdict = "PASS" if result["status"] == "pass" else f"FAIL ({result['failure_reason']})"
    print(f"MATMUL_BOARD_RESULT: {verdict} {final}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
