#!/usr/bin/env python3
"""Independent product-fit check of one board result (no board, no runner code).

  python hw/matmul_board/tests/product_fit_check.py RESULT_DIR HANDOFF_ZIP BUILD_DIR

Re-derives everything from the files themselves, with its own reference model,
and applies:
  - the app's stated import checks (FPGA_INTEGRATION_REPLY.md D1, D2, E1);
  - the acceptance list in docs/spec/BOARD_RESULT_FILE.md;
  - binding of result -> implementation manifest -> actual .bit/report files -> ZIP.
It deliberately does not import run_board.py, so a runner bug cannot hide here.
Prints one line per check and a final PRODUCT_FIT: PASS|FAIL. Known app-side
gaps (fields their validator does not accept yet) are listed as PENDING, not PASS.
"""
import hashlib
import json
import sys
import zipfile
from pathlib import Path

IDENTITY = 0x53494C01


def h(data):
    return hashlib.sha256(data).hexdigest()


def oracle(a, b, n):
    out = []
    for i in range(n):
        for j in range(n):
            s = 0
            for k in range(n):
                s += a[i * n + k] * b[k * n + j]
            out.append(s)  # INT8*INT8*8 cannot overflow INT32; checked below
    assert all(-2**31 <= x < 2**31 for x in out)
    return out


def main(result_dir, zip_path, build_dir):
    rd, bd = Path(result_dir), Path(build_dir)
    r = json.loads((rd / "board-result.json").read_text(encoding="utf-8"))
    inp = json.loads((rd / "inputs.json").read_text(encoding="utf-8"))
    zraw = Path(zip_path).read_bytes()
    z = zipfile.ZipFile(zip_path)
    zman = json.loads(z.read("manifest.json"))
    zexp = json.loads(z.read("expected.json"))
    mpath = bd / "implementation_manifest.json"
    m = json.loads(mpath.read_text(encoding="utf-8"))
    n, lanes = zman["parameters"]["N"], zman["parameters"]["LANES"]
    a, b = zexp["inputs"]["a"], zexp["inputs"]["b"]
    want = oracle(a, b, n)
    checks, pending = [], []

    def c(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    # Envelope and status
    required = ["schema_version", "runner_result_id", "parent_run_id", "status", "evidence", "recorded_at",
                "source_sha256", "build", "board", "interface_check", "run", "repeat_checks"]
    c("required fields present", all(k in r for k in required), [k for k in required if k not in r])
    c("schema_version 1", r.get("schema_version") == 1)
    c("status pass and evidence board_measured", r.get("status") == "pass" and r.get("evidence") == "board_measured",
      (r.get("status"), r.get("evidence"), r.get("failure_reason")))
    # Parent linkage (D2)
    c("parent_run_id == ZIP run_id", r.get("parent_run_id") == zman["run_id"], (r.get("parent_run_id"), zman["run_id"]))
    parent_map = {"matmul.sv": zman["files_sha256"]["hardware/matmul.sv"], "tb.sv": zman["files_sha256"]["hardware/tb.sv"]}
    c("source_sha256 == parent map exactly (incl. tb.sv)", r.get("source_sha256") == parent_map)
    c("ZIP entries match their manifest hashes",
      all(h(z.read(k)) == v for k, v in zman["files_sha256"].items()))
    # Parameters / interface
    c("N/LANES agree: ZIP, build, interface", (n, lanes) == (r["build"]["parameters"]["N"], r["build"]["parameters"]["LANES"])
      == (r["interface_check"]["compiled_n"], r["interface_check"]["compiled_lanes"]) == (m["parameters"]["N"], m["parameters"]["LANES"]))
    c("identity 0x53494c01", r["interface_check"]["identity"] == IDENTITY)
    # Inputs (D1)
    c("inputs.json == ZIP inputs", inp == {"A": a, "B": b})
    c("input_sha256 == app raw-byte rule", r["run"]["input_sha256"] == h(bytes(x & 255 for x in a + b)))
    # Outputs (E1)
    c("ZIP expected outputs == own oracle", zexp["outputs"] == want)
    c("board outputs == own oracle (first run)", r["run"]["outputs"] == want)
    c("repeat-without-reload outputs == oracle", r["repeat_checks"]["repeat_without_reload"].get("outputs") == want)
    c("reset+reload outputs == oracle", r["repeat_checks"]["reset_reload_rerun"].get("outputs") == want)
    c("output_sha256 == compact JSON rule",
      r["run"]["output_sha256"] == h(json.dumps(r["run"]["outputs"], separators=(",", ":")).encode()))
    cyc = n ** 3 // lanes
    c(f"cycles == N^3/LANES == {cyc} (all three runs, and ZIP)",
      r["run"]["cycles"] == r["repeat_checks"]["repeat_without_reload"]["cycles"]
      == r["repeat_checks"]["reset_reload_rerun"]["cycles"] == zexp["cycles"] == cyc)
    # Build binding (E1, BOARD_RESULT_FILE acceptance 7)
    bits = list(bd.glob("*.bit"))
    c("exactly one bitstream in build dir", len(bits) == 1, [p.name for p in bits])
    bit_sha = h(bits[0].read_bytes()) if bits else None
    c("actual .bit sha == manifest == result", bit_sha == m["bitstream_sha256"] == r["build"]["bitstream_sha256"])
    c("implementation_manifest_sha256 == actual manifest file", r["build"]["implementation_manifest_sha256"] == h(mpath.read_bytes()))
    c("manifest timing_met and drc_clean, result timing_met", m["timing"]["timing_met"] and m["drc_clean"] and r["build"]["timing_met"])
    rep = bd / "reports"
    c("every report hash in manifest matches the file",
      all(h((rep / k).read_bytes()) == v for k, v in m["report_sha256"].items()) and len(m["report_sha256"]) > 0)
    c("manifest artifact hashes match files",
      all(h((bd / ("summary/summary.json" if k == "summary.json" else k)).read_bytes()) == v
          for k, v in m["artifacts_sha256"].items()))
    # The bitstream was built from this ZIP's RTL
    c("built kernel == ZIP hardware/matmul.sv", m["rtl"]["sha256"]["matmul.sv"] == zman["files_sha256"]["hardware/matmul.sv"])
    c("built wrapper == ZIP integration/matmul_axi.sv", m["rtl"]["sha256"]["matmul_axi.sv"] == zman["files_sha256"]["integration/matmul_axi.sv"])
    c("result records this ZIP", (r.get("handoff") or {}).get("zip_sha256") == h(zraw))
    info = []
    if m.get("handoff"):
        # Bitstream was built from a handoff ZIP (build.py --handoff): it must be this ZIP.
        c("manifest records this ZIP and parent", m["handoff"].get("zip_sha256") == h(zraw)
          and m["handoff"].get("parent_run_id") == zman["run_id"])
        c("RTL files used by Vivado are the ZIP bytes (build/<cfg>/rtl/)",
          all((bd / "rtl" / f).is_file() and h((bd / "rtl" / f).read_bytes()) == m["rtl"]["sha256"][f]
              for f in ("matmul.sv", "matmul_axi.sv")))
    else:
        # Reuse by hash: the binding rule is the two "built ... == ZIP" checks above.
        info.append("bitstream reused: built from the pinned RTL, byte-identical to this ZIP's RTL "
                    f"(commit {m['rtl'].get('commit')})")
    c("configured clock consistent", r["build"]["configured_clock_hz"] == m["configured_clock_hz"], m["configured_clock_hz"])
    # Known app-side gaps (their reply): not failures of our side, but not accepted yet either.
    for f in ("board_revision", "kernel_version"):
        if r["board"].get(f) is None:
            pending.append(f"board.{f} is null; app validator requires a nonempty string until they change it (D5)")
    pending.append("HMAC signing/import is done by the app-side adapter (not in pushed app code yet)")

    for name, ok, detail in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  {detail}" if (detail and not ok) else ""))
    for i in info:
        print(f"INFO  {i}")
    for p in pending:
        print(f"PENDING  {p}")
    bad = [x for x in checks if not x[1]]
    print(f"PRODUCT_FIT: {'PASS' if not bad else 'FAIL'} ({len(checks) - len(bad)}/{len(checks)} checks; "
          f"{len(pending)} app-side pending)")
    return 0 if not bad else 1


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    sys.exit(main(*sys.argv[1:]))
