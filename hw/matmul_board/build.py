#!/usr/bin/env python3
"""One-command KV260 board build for the teammate's unchanged matmul_axi.

  python hw/matmul_board/build.py --lanes 1            # N=8, LANES=1
  python hw/matmul_board/build.py --lanes 4            # N=8, LANES=4 (separate folder)
  python hw/matmul_board/build.py --compare            # side-by-side summary of both

Steps: verify the pinned RTL hashes; run build.tcl in Vivado batch mode with the
working directory inside build/n<N>_l<LANES>/ (keeps Vivado scratch files out of
the repo); collect post-route reports with hw/tools/collect_reports.tcl;
summarize them with hw/tools/vivado_summary.py; judge timing/DRC from those
reports; write implementation_manifest.json binding sources, parameters, clock,
address map, report hashes and artifact hashes. Standard library only.

A passing build means implemented + timing met. It is not evidence that the
bitstream was loaded or executed on a board.
"""
import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
TOOLS = REPO / "hw" / "tools"
VIVADO = Path(r"C:/AMDDesignTools/2025.2/Vivado/bin/vivado.bat")
RTL_COMMIT = "84fcae1000f056f869b6b84a28804b98cb7b6a48"
RTL_ORIGIN = "origin/codex/siliconos-demo (identical files on origin/codex/ai-rtl-generation b8d9fca)"
PINNED = {
    "matmul.sv": "f81498d1fdb9a73a32e7f70a5d55c09b6198d2f03f00ab27d9099a63d82f418c",
    "matmul_axi.sv": "26d5eca5ea16bf81336cece4f9a76617cfaf5444cc4b92a734a656cff4dc080c",
}
KERNEL_INSTANCE = "u_matmul"
SCHEMA = "fabzero.matmul_board.implementation_manifest/1"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(path):
    return Path(path).resolve().relative_to(REPO).as_posix()


def verify_rtl():
    for name, want in PINNED.items():
        got = sha256(HERE / "rtl" / name)
        if got != want:
            sys.exit(f"RTL hash mismatch for rtl/{name}: {got} != pinned {want}. Refusing to build.")
    print("RTL hashes match the pinned commit", RTL_COMMIT)


def run(cmd, cwd, console, timeout):
    print(">", " ".join(str(c) for c in cmd), f"(cwd {cwd})", flush=True)
    with open(console, "w", encoding="utf-8", errors="replace") as fh:
        p = subprocess.run([str(c) for c in cmd], cwd=cwd, stdout=fh, stderr=subprocess.STDOUT,
                           timeout=timeout)
    return p.returncode


def read_kv(path):
    out = {}
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def git_state():
    def g(*args):
        return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout.strip()
    return {"fabzero_head": g("rev-parse", "HEAD"),
            "matmul_board_paths_status": g("status", "--porcelain", "--untracked-files=all",
                                           "--", "hw/matmul_board", ":!hw/matmul_board/build",
                                           ":!hw/matmul_board/results").splitlines()}


def judge(summary, info, out):
    """Return (timing_met, findings) from the reports. Every check must pass."""
    s = summary["summaries"][0]
    t = s.get("timing", {})
    findings = []
    met = t.get("constraints_met") is True
    if not met:
        findings.append(f"timing report constraints_met={t.get('constraints_met')}")
    for key in ("WNS", "WHS", "WPWS"):
        v = t.get(key)
        if not isinstance(v, (int, float)) or v < 0:
            met = False
            findings.append(f"{key}={v}")
    for key in ("TNS_failing", "THS_failing", "TPWS_failing"):
        v = t.get(key)
        if v not in (0, None):
            met = False
            findings.append(f"{key}={v}")
    for key in ("impl_WNS", "impl_WHS"):
        try:
            if float(info.get(key, "nan")) < 0:
                met = False
                findings.append(f"run property {key}={info.get(key)}")
        except ValueError:
            met = False
            findings.append(f"run property {key} unreadable: {info.get(key)}")
    route = (out / "reports" / "route_status.rpt").read_text(errors="replace")
    m = re.search(r"# of nets with routing errors\.*\s*:\s*(\d+)", route)
    if not m or int(m.group(1)) != 0:
        met = False
        findings.append("route status: routing errors or unreadable route_status.rpt")
    drc = s.get("checks", {}).get("drc", {}).get("by_severity", {})
    drc_errors = sum(v for k, v in drc.items() if k.lower() in ("error", "critical warning"))
    if drc_errors:
        findings.append(f"DRC errors/critical warnings: {drc}")
    return met, drc_errors == 0, findings


def build(n, lanes, force, stage, handoff=None, handoff_path=None):
    if handoff is None:
        verify_rtl()
    tag = f"n{n}_l{lanes}"
    out = HERE / "build" / tag
    if out.exists():
        if not force:
            sys.exit(f"{rel(out)} exists; pass --force to delete and rebuild it.")
        shutil.rmtree(out)
    out.mkdir(parents=True)
    started = dt.datetime.now().astimezone()
    rtldir = HERE / "rtl"
    if handoff is not None:
        # Build from the RTL inside the app's handoff ZIP, never from rtl/.
        rtldir = out / "rtl"
        rtldir.mkdir()
        for name, data in handoff["rtl_bytes"].items():
            (rtldir / name).write_bytes(data)
        print(f"building from handoff ZIP RTL: parent run {handoff['parent_run_id']}, "
              f"matmul.sv {sha256(rtldir / 'matmul.sv')[:16]}, matmul_axi.sv {sha256(rtldir / 'matmul_axi.sv')[:16]}")

    rc = run([VIVADO, "-mode", "batch", "-nojournal", "-log", out / "vivado_build.log",
              "-source", HERE / "build.tcl", "-tclargs", n, lanes, out, stage, rtldir],
             out, out / "console_build.txt", 3 * 3600)
    log = (out / "vivado_build.log").read_text(errors="replace") if (out / "vivado_build.log").exists() else ""
    done = "BUILD_DONE" if stage == "full" else "BD_DONE"
    if rc != 0 or done not in log:
        sys.exit(f"Vivado build failed (exit {rc}); see {rel(out / 'vivado_build.log')}")
    if stage == "bd":
        print((out / "build_info.txt").read_text())
        return

    rc = run([VIVADO, "-mode", "batch", "-nojournal", "-log", out / "vivado_reports.log",
              "-source", TOOLS / "collect_reports.tcl", "-tclargs",
              out / "proj" / "matmul_board.xpr", out / "reports", KERNEL_INSTANCE],
             out, out / "console_reports.txt", 3600)
    if rc != 0 or "COLLECT_DONE" not in (out / "vivado_reports.log").read_text(errors="replace"):
        sys.exit(f"report collection failed (exit {rc}); see {rel(out / 'vivado_reports.log')}")

    cycles = n ** 3 // lanes
    synth_log = out / "proj" / "matmul_board.runs" / "synth_1" / "runme.log"
    rc = subprocess.run([sys.executable, TOOLS / "vivado_summary.py", out / "reports",
                         "--kernel", KERNEL_INSTANCE, "--n", str(n), "--cycles", str(cycles),
                         "--cycles-source", "expected", "--log", synth_log,
                         "--label", f"N={n} LANES={lanes} post-route",
                         "--title", f"matmul_board N={n} LANES={lanes} post-route",
                         "--out", out / "summary"]).returncode
    if rc != 0:
        sys.exit("vivado_summary.py failed")
    summary = json.loads((out / "summary" / "summary.json").read_text(encoding="utf-8"))
    info = read_kv(out / "build_info.txt")
    timing_met, drc_clean, findings = judge(summary, info, out)

    bit = out / f"matmul_board_{tag}.bit"
    xsa = out / f"matmul_board_{tag}.xsa"
    t = summary["summaries"][0]["timing"]
    manifest = {
        "schema": SCHEMA,
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "build_started_at": started.isoformat(timespec="seconds"),
        "task": "MATMUL-BOARD-001",
        "vivado_version": info.get("vivado"),
        "target_part": info.get("part"),
        "board_part": info.get("board_part"),
        "logical_top": "matmul_axi",
        "board_top": info.get("board_top"),
        "kernel_instance": KERNEL_INSTANCE,
        "parameters": {"N": n, "LANES": lanes},
        "elaborated_parameters": {"N": info.get("elaborated_N"), "LANES": info.get("elaborated_LANES")},
        "configured_clock_hz": int(info["pl_clk0_freq_hz"]),
        "clock_source": "zynq_ultra_ps_e_0/pl_clk0 (KV260 board preset), constraint from the PS IP",
        "reset": "rst_pl_clk0 (proc_sys_reset) peripheral_aresetn, synchronous to pl_clk0",
        "address_map": {"segment": info.get("address_segment"),
                        "base_address": info.get("base_address"),
                        "range": info.get("address_range"),
                        "decoded_bits": "matmul_axi decodes address[7:0]; map repeats every 0x100 in the segment"},
        "expected_compute_cycles": cycles,
        "rtl": {"commit": RTL_COMMIT if handoff is None else None,
                "origin": RTL_ORIGIN if handoff is None else "app handoff ZIP (build/<cfg>/rtl/)",
                "sha256": {name: sha256(rtldir / name) for name in PINNED},
                "matches_pinned_commit": all(sha256(rtldir / k) == v for k, v in PINNED.items())},
        "handoff": None if handoff is None else {
            "zip_sha256": handoff["zip_sha256"], "zip_name": Path(handoff_path).name,
            "parent_run_id": handoff["parent_run_id"], "source_evidence": handoff["source_evidence"],
            "parent_source_sha256": handoff["parent_source_sha256"]},
        "build_sources_sha256": {rel(p): sha256(p) for p in
                                 [HERE / "matmul_board_top.sv", HERE / "build.tcl", HERE / "build.py",
                                  TOOLS / "collect_reports.tcl", TOOLS / "vivado_summary.py"]},
        "repository": git_state(),
        "timing": {"timing_met": timing_met, "constraints_met": t.get("constraints_met"),
                   "WNS_ns": t.get("WNS"), "TNS_ns": t.get("TNS"), "WHS_ns": t.get("WHS"),
                   "THS_ns": t.get("THS"), "WPWS_ns": t.get("WPWS"), "TPWS_ns": t.get("TPWS"),
                   "failing_endpoints": {k: t.get(k) for k in ("TNS_failing", "THS_failing", "TPWS_failing")},
                   "findings": findings},
        "drc_clean": drc_clean,
        "drc_by_severity": summary["summaries"][0].get("checks", {}).get("drc", {}).get("by_severity"),
        "methodology_by_severity": summary["summaries"][0].get("checks", {}).get("methodology", {}).get("by_severity"),
        "report_sha256": {p.name: sha256(p) for p in sorted((out / "reports").glob("*")) if p.is_file()},
        "artifacts_sha256": {p.name: sha256(p) for p in
                             [bit, xsa, out / "psu_init.tcl", out / "addresses.tcl",
                              out / "build_info.txt", out / "matmul_board_bd_export.tcl",
                              out / "summary" / "summary.json"]},
        "bitstream_sha256": sha256(bit),
        "limitations": [
            "Implementation evidence only: no board load or execution is implied.",
            "Cycle count is the checked-in schedule expectation (N^3/LANES), not a measurement.",
            "configured_clock_hz is the PS PLL setting from the block design; actual board frequency is unmeasured.",
        ],
    }
    mpath = out / "implementation_manifest.json"
    mpath.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    msha = sha256(mpath)
    (out / "implementation_manifest.sha256").write_text(f"{msha}  implementation_manifest.json\n")
    verdict = "PASS" if timing_met and drc_clean else "FAIL"
    print(f"BUILD_RESULT {tag}: {verdict} timing_met={timing_met} drc_clean={drc_clean} "
          f"WNS={t.get('WNS')} WHS={t.get('WHS')} WPWS={t.get('WPWS')} "
          f"base={info.get('base_address')} clock_hz={info.get('pl_clk0_freq_hz')}")
    print(f"bitstream {rel(bit)} sha256 {manifest['bitstream_sha256']}")
    print(f"manifest  {rel(mpath)} sha256 {msha}")
    for f in findings:
        print("  finding:", f)
    if verdict != "PASS":
        sys.exit(1)


def compare(n):
    dirs = [HERE / "build" / f"n{n}_l{l}" / "reports" for l in (1, 4)]
    for d in dirs:
        if not d.is_dir():
            sys.exit(f"missing {rel(d)}; build both lane counts first")
    out = HERE / "build" / f"compare_n{n}"
    sys.exit(subprocess.run([sys.executable, TOOLS / "vivado_summary.py", *dirs,
                             "--kernel", KERNEL_INSTANCE, "--n", str(n),
                             "--cycles", str(n ** 3), "--cycles", str(n ** 3 // 4),
                             "--cycles-source", "expected",
                             "--label", f"N={n} LANES=1", "--label", f"N={n} LANES=4",
                             "--title", f"matmul_board N={n}: 1 lane vs 4 lanes (post-route)",
                             "--out", out]).returncode)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=8, choices=[8, 16])
    ap.add_argument("--lanes", type=int, choices=[1, 4])
    ap.add_argument("--stage", default="full", choices=["full", "bd"],
                    help="bd = block design and address map only (quick check)")
    ap.add_argument("--force", action="store_true", help="delete an existing output folder first")
    ap.add_argument("--compare", action="store_true", help="compare existing LANES=1 and LANES=4 builds")
    ap.add_argument("--handoff", help="build from the RTL inside this app handoff ZIP (N/LANES from the ZIP)")
    a = ap.parse_args()
    if a.compare:
        compare(a.n)
    elif a.handoff:
        sys.path.insert(0, str(HERE))
        import run_board
        try:
            h = run_board.load_handoff(a.handoff)
        except (ValueError, OSError, json.JSONDecodeError, UnicodeDecodeError) as e:
            sys.exit(f"refusing handoff ZIP: {e}")
        if a.lanes is not None and a.lanes != h["LANES"]:
            sys.exit(f"--lanes {a.lanes} differs from the ZIP's LANES={h['LANES']}")
        build(h["N"], h["LANES"], a.force, a.stage, h, a.handoff)
    elif a.lanes is None:
        ap.error("--lanes is required unless --compare or --handoff")
    else:
        build(a.n, a.lanes, a.force, a.stage)


if __name__ == "__main__":
    main()
