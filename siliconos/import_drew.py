"""Verify and import one Drew KV260 result into the local SiliconOS server.

Run with SILICONOS_RUNNER_KEY and SILICONOS_RUNNER_KEY_ID set in the shell.
The signed JSON stays local; the source result folder is never rewritten.
"""
import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path

from .board_adapter import adapt_drew_result


def main():
    parser = argparse.ArgumentParser(description="Verify, sign and import an app-linked KV260 board result")
    parser.add_argument("result", type=Path, help="Drew result folder or board-result.json")
    parser.add_argument("build", type=Path, help="Matching build/n8_l1 or build/n8_l4 folder")
    parser.add_argument("handoff", type=Path, help="Original SiliconOS handoff ZIP")
    parser.add_argument("--server", default="http://127.0.0.1:8000", help="Local SiliconOS server")
    args = parser.parse_args()
    result_file = args.result / "board-result.json" if args.result.is_dir() else args.result
    try:
        signed = adapt_drew_result(result_file, args.build, args.handoff)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        parser.exit(1, f"Import preparation failed: {exc}\n")
    parent_id = signed["parent_run_id"]
    request = urllib.request.Request(
        f"{args.server.rstrip('/')}/api/runs/{parent_id}/board-result",
        data=json.dumps(signed, separators=(",", ":")).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            imported = json.load(response)
    except urllib.error.HTTPError as exc:
        message = exc.read().decode(errors="replace")
        parser.exit(1, f"Import rejected ({exc.code}): {message}\n")
    if imported.get("evidence") != "board_measured" or imported.get("correct") is not True:
        parser.exit(1, "Server returned no accepted board measurement.\n")
    print(f"Accepted board measurement {imported['id']} for parent {parent_id}")
    print(f"Bitstream SHA-256: {imported['build']['bitstream_sha256']}")


if __name__ == "__main__":
    main()
