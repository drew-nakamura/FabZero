#!/usr/bin/env python3
"""Sign a passing KV260 board result and import it into the local SiliconOS app.

  python hw/matmul_board/sign_result.py results/<run_id>                 # sign + POST to 127.0.0.1:8000
  python hw/matmul_board/sign_result.py results/<run_id> --out FILE      # sign only, write the envelope

Before signing it re-verifies, from the files on disk: the result is a passing
board_measured run with a parent; build/n<N>_l<LANES>/implementation_manifest.json
hashes to the value in the result; the .bit file and every report and artifact
hash match that manifest. It then signs {board_result, inputs, manifest text,
summary text} with HMAC-SHA256 (siliconos.board.sign; key from
SILICONOS_RUNNER_KEY / SILICONOS_RUNNER_KEY_ID). The result folder is never edited.
"""
import argparse
import datetime as dt
import hashlib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from siliconos import board  # noqa: E402


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build_payload(result_dir, build_root=HERE / "build"):
    rd = Path(result_dir)
    r = json.loads((rd / "board-result.json").read_text(encoding="utf-8"))
    inputs = json.loads((rd / "inputs.json").read_text(encoding="utf-8"))
    if r.get("status") != "pass" or r.get("evidence") != "board_measured":
        raise ValueError(f"refusing to sign: status={r.get('status')} evidence={r.get('evidence')} "
                         f"({r.get('failure_reason')})")
    if not r.get("parent_run_id"):
        raise ValueError("refusing to sign: result has no parent_run_id (run it with run_board.py --handoff)")
    p = r["build"]["parameters"]
    bd = Path(build_root) / f"n{p['N']}_l{p['LANES']}"
    mpath = bd / "implementation_manifest.json"
    mtext_bytes = mpath.read_bytes()
    if hashlib.sha256(mtext_bytes).hexdigest() != r["build"]["implementation_manifest_sha256"]:
        raise ValueError(f"refusing to sign: {mpath} is not the manifest this result was run with")
    m = json.loads(mtext_bytes)
    bits = list(bd.glob("*.bit"))
    if len(bits) != 1 or sha(bits[0]) != m["bitstream_sha256"] or m["bitstream_sha256"] != r["build"]["bitstream_sha256"]:
        raise ValueError("refusing to sign: bitstream file does not match the manifest/result")
    for name, want in m["report_sha256"].items():
        if sha(bd / "reports" / name) != want:
            raise ValueError(f"refusing to sign: report {name} does not match the manifest")
    for name, want in m["artifacts_sha256"].items():
        path = bd / "summary" / name if name == "summary.json" else bd / name
        if sha(path) != want:
            raise ValueError(f"refusing to sign: artifact {name} does not match the manifest")
    return {
        "board_result": r,
        "inputs": inputs,
        "implementation_manifest": mtext_bytes.decode("utf-8"),
        "implementation_summary": (bd / "summary" / "summary.json").read_bytes().decode("utf-8"),
        "signer": {"tool": "hw/matmul_board/sign_result.py", "bitstream_sha256": sha(bits[0]),
                   "reports_verified": True, "result_folder": rd.name},
        "signed_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("result_dir")
    ap.add_argument("--app", default="http://127.0.0.1:8000", help="local SiliconOS server")
    ap.add_argument("--out", help="write the signed envelope here instead of posting")
    a = ap.parse_args(argv)
    try:
        payload = build_payload(a.result_dir)
        envelope = board.sign(payload)
    except (ValueError, OSError, KeyError) as e:
        sys.exit(f"SIGN_RESULT: FAIL {e}")
    if a.out:
        Path(a.out).write_text(json.dumps(envelope), encoding="utf-8")
        print(f"SIGN_RESULT: signed -> {a.out}")
        return 0
    parent = payload["board_result"]["parent_run_id"]
    req = urllib.request.Request(f"{a.app}/api/runs/{parent}/board-result", data=json.dumps(envelope).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            child = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"IMPORT: FAIL HTTP {e.code} {e.read().decode(errors='replace')}")
    except urllib.error.URLError as e:
        sys.exit(f"IMPORT: FAIL cannot reach {a.app} ({e.reason}); is `python server.py` running?")
    note = " (already imported)" if child.get("already_imported") else ""
    print(f"IMPORT: OK board run {child['id']} for parent {parent}: {child['cycles']} cycles, "
          f"{len(child['outputs'])} outputs verified{note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
