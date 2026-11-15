"""KV260 board-result import: HMAC verification and deterministic acceptance.

A trusted signer on the board laptop (hw/matmul_board/sign_result.py) re-hashes
the bitstream/reports, wraps the runner's board-result.json plus the bound
implementation manifest in a payload and signs it with HMAC-SHA256. The server
verifies the signature, then re-checks everything against the stored parent run
with its own reference model before saving a separate board_measured child run.
The parent run is never modified. Failed or replayed results are never accepted.

Key: SILICONOS_RUNNER_KEY (hex, >= 32 bytes) and SILICONOS_RUNNER_KEY_ID in the
environment of the signer and the server only. Never in Git, JSON or the browser.
"""
import hashlib
import hmac
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .engine import reference

SCHEMA = "siliconos.board_import/1"
IDENTITY = 0x53494C01
BOARD_CHECK_MAX_AGE_S = 300


def canonical(obj):
    """Bytes that are signed: sorted keys, compact separators, UTF-8."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def runner_key():
    key_hex, key_id = os.environ.get("SILICONOS_RUNNER_KEY"), os.environ.get("SILICONOS_RUNNER_KEY_ID")
    if not key_hex or not key_id:
        raise ValueError("Board import is not configured: set SILICONOS_RUNNER_KEY and SILICONOS_RUNNER_KEY_ID "
                         "for the signer and the server.")
    try:
        key = bytes.fromhex(key_hex)
    except ValueError:
        raise ValueError("SILICONOS_RUNNER_KEY must be hexadecimal.")
    if len(key) < 32:
        raise ValueError("SILICONOS_RUNNER_KEY must be at least 32 bytes (64 hex characters).")
    return key, key_id


def sign(payload, key=None, key_id=None):
    if key is None:
        key, key_id = runner_key()
    return {"schema": SCHEMA, "key_id": key_id, "payload": payload,
            "hmac_sha256": hmac.new(key, canonical(payload), hashlib.sha256).hexdigest()}


def verify(envelope, key=None, key_id=None):
    if key is None:
        key, key_id = runner_key()
    if not isinstance(envelope, dict) or envelope.get("schema") != SCHEMA:
        raise ValueError("Not a signed SiliconOS board result.")
    if envelope.get("key_id") != key_id:
        raise ValueError("Board result was signed with an unknown runner key.")
    mac = envelope.get("hmac_sha256")
    want = hmac.new(key, canonical(envelope.get("payload")), hashlib.sha256).hexdigest()
    if not isinstance(mac, str) or not hmac.compare_digest(mac, want):
        raise ValueError("Board result signature is invalid. Nothing was imported.")
    return envelope["payload"]


def _require(ok, message):
    if not ok:
        raise ValueError("Board result rejected: " + message)


def accept(parent, envelope, wrapper_sha256, key=None, key_id=None):
    """Verify and check a signed board result against its parent run.
    Returns the new board_measured child record (not yet saved)."""
    p = verify(envelope, key, key_id)
    r, inputs = p.get("board_result"), p.get("inputs")
    mtext, stext = p.get("implementation_manifest"), p.get("implementation_summary")
    _require(isinstance(r, dict) and isinstance(inputs, dict) and isinstance(mtext, str), "payload is incomplete")
    _require(r.get("schema_version") == 1, "unsupported board-result schema")
    _require(r.get("status") == "pass" and r.get("evidence") == "board_measured" and not r.get("failure_reason"),
             "only passing board_measured runs can be imported")
    # Parent: checked-in RTL simulation for the KV260 (board demo scope: N=8, LANES 1/4).
    spec = parent.get("spec") or {}
    _require(parent.get("correct") is True and parent.get("evidence") == "rtl_simulation",
             "parent must be a verified checked-in RTL simulation run")
    _require(spec.get("target") == "kv260", "parent run does not target the KV260")
    _require(r.get("parent_run_id") == parent.get("id"), "result belongs to a different parent run")
    n, lanes = spec.get("size"), parent.get("lanes")
    build, iface, run = r.get("build") or {}, r.get("interface_check") or {}, r.get("run") or {}
    _require(n == 8 and lanes in (1, 4), "board demo supports N=8 with 1 or 4 lanes")
    _require(build.get("parameters") == {"N": n, "LANES": lanes}
             and (iface.get("compiled_n"), iface.get("compiled_lanes")) == (n, lanes), "N/LANES mismatch")
    _require(iface.get("identity") == IDENTITY and iface.get("scratch_register_ok") is True, "interface check failed")
    # Sources and inputs must be the parent's own.
    _require(r.get("source_sha256") == parent.get("source_sha256"), "source hashes differ from the parent run")
    a, b = (parent.get("inputs") or {}).get("a"), (parent.get("inputs") or {}).get("b")
    _require(inputs == {"A": a, "B": b}, "board inputs differ from the parent run")
    raw = sha256(bytes(x & 255 for x in a + b))
    _require(run.get("input_sha256") == raw == parent.get("input_sha256"), "input hash mismatch")
    # Outputs: independent reference, parent outputs, all three board runs.
    want = reference(a, b, n)
    outs = run.get("outputs")
    _require(outs == want == parent.get("outputs"), "board outputs do not match the reference")
    _require(run.get("output_sha256") == sha256(json.dumps(outs, separators=(",", ":")).encode()),
             "output hash mismatch")
    reps = r.get("repeat_checks") or {}
    for name in ("repeat_without_reload", "reset_reload_rerun"):
        rep = reps.get(name) or {}
        _require(rep.get("outputs_match") is True and rep.get("outputs") == want, f"{name} outputs mismatch")
    cycles = n ** 3 // lanes
    _require(run.get("cycles") == cycles == parent.get("cycles")
             and all((reps.get(k) or {}).get("cycles") == cycles for k in ("repeat_without_reload", "reset_reload_rerun")),
             f"cycle count must be {cycles} on every run")
    # Build binding: manifest bytes, bitstream, timing, RTL, wrapper.
    _require(sha256(mtext.encode("utf-8")) == build.get("implementation_manifest_sha256"),
             "implementation manifest does not match its recorded hash")
    m = json.loads(mtext)
    _require(m.get("bitstream_sha256") == build.get("bitstream_sha256"), "bitstream hash differs from the manifest")
    _require((m.get("timing") or {}).get("timing_met") is True and m.get("drc_clean") is True
             and build.get("timing_met") is True, "implementation did not meet timing / DRC")
    _require(m.get("parameters") == {"N": n, "LANES": lanes}, "manifest parameters mismatch")
    rtl = (m.get("rtl") or {}).get("sha256") or {}
    _require(rtl.get("matmul.sv") == parent["source_sha256"].get("matmul.sv"),
             "bitstream was not built from the parent's matmul.sv")
    _require(rtl.get("matmul_axi.sv") == wrapper_sha256 == r.get("wrapper_sha256"),
             "bitstream wrapper differs from this app's matmul_axi.sv")
    _require(m.get("configured_clock_hz") == build.get("configured_clock_hz"), "clock mismatch")
    signer = p.get("signer") or {}
    _require(signer.get("bitstream_sha256") == m.get("bitstream_sha256") and signer.get("reports_verified") is True,
             "signer did not verify the bitstream and report files")
    area = None
    if isinstance(stext, str):
        _require(sha256(stext.encode("utf-8")) == (m.get("artifacts_sha256") or {}).get("summary.json"),
                 "implementation summary does not match the manifest")
        s = json.loads(stext)["summaries"][0]
        area = {k: s["area"].get(k) for k in ("Total LUTs", "FFs", "DSP Blocks", "RAMB36", "RAMB18")}
        area["scope"] = s.get("area_scope")
    try:
        uuid.UUID(str(r.get("runner_result_id")))
    except ValueError:
        raise ValueError("Board result rejected: runner_result_id is not a UUID")

    clock = m["configured_clock_hz"]
    t = m.get("timing") or {}
    return {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "evidence": "board_measured", "correct": True, "physical_fpga": True, "physical_asic": False,
        "parent_run_id": parent["id"], "runner_result_id": r["runner_result_id"],
        "runner_result_folder": signer.get("result_folder") if re.fullmatch(
            r"\d{8}T\d{6}Z_n8_l[14](?:-\d+)?", str(signer.get("result_folder"))) else None,
        "spec": spec, "lanes": lanes, "seed": parent.get("seed"), "parameters": {"N": n, "LANES": lanes},
        "cycles": run["cycles"], "kernel_time_us": round(run["cycles"] / clock * 1e6, 3),
        "clock_status": "configured PS clock from the implementation manifest; not measured on the board",
        "configured_clock_hz": clock,
        "inputs": parent["inputs"], "outputs": outs, "input_sha256": raw, "output_sha256": run["output_sha256"],
        "source_sha256": r["source_sha256"], "wrapper_sha256": r["wrapper_sha256"],
        "repeat_checks": {k: {"outputs_match": True, "cycles": cycles} for k in ("repeat_without_reload", "reset_reload_rerun")},
        "host_elapsed_ns": run.get("host_elapsed_ns"), "programming_elapsed_ns": run.get("programming_elapsed_ns"),
        "recorded_at": r.get("recorded_at"), "board": r.get("board"), "interface_check": iface,
        "build": {**build, "timing": {k: t.get(k) for k in ("WNS_ns", "WHS_ns", "WPWS_ns")},
                  "target_part": m.get("target_part"), "address_map": m.get("address_map")},
        "resources": area,
        "handoff_zip_sha256": (r.get("handoff") or {}).get("zip_sha256"),
        "board_import": {"key_id": envelope["key_id"], "signed_at": p.get("signed_at"),
                         "envelope_sha256": sha256(canonical(envelope))},
        "limitations": [
            "Measured on one AMD Kria KV260 over JTAG for this run's exact inputs; not a proof for every input.",
            "Kernel cycles come from the accelerator's busy counter; kernel time uses the configured clock (not measured).",
            "Host transfer and programming times are JTAG/debugger times and are not accelerator speed.",
            "Resources come from the Vivado report bound to this bitstream; power is not measured.",
        ],
    }


def board_status(check_file, max_age_s=BOARD_CHECK_MAX_AGE_S):
    """Board availability from run_board.py --check: available only if a passing
    check is at most max_age_s old. Anything else is reported as unknown."""
    path = Path(check_file)
    out = {"available": False, "checked_at": None, "age_seconds": None, "cable_serial": None,
           "last_check_ok": False, "reason": "no board check yet (python hw/matmul_board/run_board.py --check)"}
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
        checked = datetime.fromisoformat(rec["checked_at"])
        age = (datetime.now(timezone.utc) - checked).total_seconds()
    except (OSError, ValueError, KeyError, TypeError):
        return out
    out.update(checked_at=rec["checked_at"], age_seconds=round(age), cable_serial=rec.get("cable_serial"),
               last_check_ok=bool(rec.get("ok")))
    if not rec.get("ok"):
        out["reason"] = rec.get("reason") or "last board check failed"
    elif age > max_age_s or age < -60:
        out["reason"] = f"last board check is {round(age)} s old (needs <= {max_age_s} s)"
    else:
        out.update(available=True, reason=None)
    return out
