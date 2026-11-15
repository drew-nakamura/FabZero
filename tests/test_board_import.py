"""KV260 board-result import: signing, acceptance, idempotency, status, HTTP.

Positive cases use the real board results measured on 2026-11-14 for the app's
exported runs (hw/matmul_board/results/2026111{5T011930Z_n8_l1,5T012007Z_n8_l4})
and parents rebuilt from the committed handoff ZIPs in data/handoff_exports.
"""
import copy
import hashlib
import json
import os
import secrets
import shutil
import tempfile
import threading
import unittest
import zipfile
from datetime import datetime, timedelta, timezone
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

import server
from siliconos import board
from siliconos.engine import DEFAULT

ROOT = Path(__file__).resolve().parents[1]
HW = ROOT / "hw" / "matmul_board"
import sys
sys.path.insert(0, str(HW))
import sign_result  # noqa: E402

RUNS = {1: ("20261115T011930Z_n8_l1", "6bccf63e-f83a-4e12-88e6-78b20d120b65"),
        4: ("20261115T012007Z_n8_l4", "3abe54e6-25d2-4eb7-90bf-dd3b39f3a4e9")}
KEY, KID = secrets.token_bytes(32), "test-key"
WRAPPER = hashlib.sha256((ROOT / "hardware" / "matmul_axi.sv").read_bytes()).hexdigest()


def parent(lanes):
    """The app run record behind a committed handoff ZIP (as the app stored it)."""
    folder, run_id = RUNS[lanes]
    z = zipfile.ZipFile(next((ROOT / "data" / "handoff_exports").glob(f"siliconos-{run_id}-*-handoff.zip")))
    m, e = json.loads(z.read("manifest.json")), json.loads(z.read("expected.json"))
    a, b = e["inputs"]["a"], e["inputs"]["b"]
    return {"id": run_id, "evidence": "rtl_simulation", "correct": True, "spec": dict(DEFAULT), "lanes": lanes,
            "seed": 42, "cycles": e["cycles"], "inputs": {"a": a, "b": b}, "outputs": e["outputs"],
            "input_sha256": hashlib.sha256(bytes(x & 255 for x in a + b)).hexdigest(),
            "source_sha256": {"matmul.sv": m["files_sha256"]["hardware/matmul.sv"],
                              "tb.sv": m["files_sha256"]["hardware/tb.sv"]},
            "created_at": "2026-11-14T00:00:00+00:00"}


def payload(lanes):
    return sign_result.build_payload(HW / "results" / RUNS[lanes][0])


def accept(par, env, wrapper=WRAPPER):
    return board.accept(par, env, wrapper, KEY, KID)


class Acceptance(unittest.TestCase):
    def test_real_board_results_are_accepted(self):
        for lanes in (1, 4):
            with self.subTest(lanes=lanes):
                par = parent(lanes)
                child = accept(par, board.sign(payload(lanes), KEY, KID))
                self.assertEqual((child["evidence"], child["physical_fpga"], child["parent_run_id"]),
                                 ("board_measured", True, par["id"]))
                self.assertEqual(child["cycles"], 512 // lanes)
                self.assertEqual(child["outputs"], par["outputs"])
                self.assertEqual(child["configured_clock_hz"], 99999001)
                self.assertAlmostEqual(child["kernel_time_us"], (512 // lanes) / 99.999001, places=3)
                self.assertEqual(child["resources"]["DSP Blocks"], 0)
                self.assertEqual(child["resources"]["Total LUTs"], 354 if lanes == 1 else 3612)
                self.assertNotEqual(child["id"], par["id"])

    def test_signature_and_key_are_enforced(self):
        env = board.sign(payload(1), KEY, KID)
        bad = copy.deepcopy(env)
        bad["payload"]["board_result"]["run"]["cycles"] = 1
        with self.assertRaisesRegex(ValueError, "signature is invalid"):
            accept(parent(1), bad)
        with self.assertRaisesRegex(ValueError, "unknown runner key"):
            board.accept(parent(1), env, WRAPPER, KEY, "other-key")
        with self.assertRaisesRegex(ValueError, "signature is invalid"):
            board.accept(parent(1), env, WRAPPER, secrets.token_bytes(32), KID)
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "not configured"):
                board.accept(parent(1), env, WRAPPER)

    def test_signed_but_wrong_content_is_rejected(self):
        def mutate(fn, par=None, wrapper=WRAPPER):
            p = payload(1)
            fn(p)
            return lambda: accept(par or parent(1), board.sign(p, KEY, KID), wrapper)
        cases = [
            (lambda p: p["board_result"]["run"]["outputs"].__setitem__(3, 0), "outputs do not match"),
            (lambda p: p["board_result"]["repeat_checks"]["reset_reload_rerun"]["outputs"].__setitem__(0, 7),
             "reset_reload_rerun outputs mismatch"),
            (lambda p: p["board_result"]["run"].__setitem__("cycles", 513), "cycle count"),
            (lambda p: p["board_result"].__setitem__("status", "fail"), "only passing"),
            (lambda p: p["board_result"].__setitem__("evidence", "replay_test_not_board"), "only passing"),
            (lambda p: p["board_result"].__setitem__("parent_run_id", RUNS[4][1]), "different parent"),
            (lambda p: p["inputs"]["A"].__setitem__(0, 1), "inputs differ"),
            (lambda p: p.__setitem__("implementation_manifest", p["implementation_manifest"] + " "), "manifest does not match"),
            (lambda p: p.__setitem__("implementation_summary", p["implementation_summary"] + " "), "summary does not match"),
            (lambda p: p["signer"].__setitem__("reports_verified", False), "signer did not verify"),
            (lambda p: p["board_result"]["interface_check"].__setitem__("identity", 0), "interface check"),
        ]
        for fn, needle in cases:
            with self.subTest(needle=needle):
                with self.assertRaisesRegex(ValueError, needle):
                    mutate(fn)()
        par = parent(1)
        par["source_sha256"] = {**par["source_sha256"], "tb.sv": "0" * 64}
        with self.assertRaisesRegex(ValueError, "source hashes differ"):
            mutate(lambda p: None, par)()
        with self.assertRaisesRegex(ValueError, "wrapper differs"):
            mutate(lambda p: None, wrapper="1" * 64)()
        par = parent(1)
        par["evidence"] = "ai_generated_rtl"
        with self.assertRaisesRegex(ValueError, "checked-in RTL"):
            mutate(lambda p: None, par)()
        par = parent(1)
        par["lanes"] = 4
        with self.assertRaisesRegex(ValueError, "N/LANES"):
            mutate(lambda p: None, par)()

    def test_signer_refuses_unverifiable_results(self):
        with tempfile.TemporaryDirectory() as td:
            res = Path(td) / "r"
            shutil.copytree(HW / "results" / RUNS[1][0], res)
            r = json.loads((res / "board-result.json").read_text())
            r["status"] = "fail"
            (res / "board-result.json").write_text(json.dumps(r))
            with self.assertRaisesRegex(ValueError, "refusing to sign"):
                sign_result.build_payload(res)
            build = Path(td) / "build"
            shutil.copytree(HW / "build" / "n8_l1", build / "n8_l1", ignore=shutil.ignore_patterns("proj", "rtl"))
            rpt = build / "n8_l1" / "reports" / "timing_summary.rpt"
            rpt.write_bytes(rpt.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "report timing_summary.rpt"):
                sign_result.build_payload(HW / "results" / RUNS[1][0], build_root=build)


class BoardStatus(unittest.TestCase):
    def test_freshness_rules(self):
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "board_check.json"
            self.assertFalse(board.board_status(f)["available"])
            now = datetime.now(timezone.utc)
            for ok, age, want in [(True, 10, True), (True, 400, False), (False, 10, False)]:
                f.write_text(json.dumps({"ok": ok, "checked_at": (now - timedelta(seconds=age)).isoformat(),
                                         "cable_serial": "X", "reason": None if ok else "no cable"}))
                with self.subTest(ok=ok, age=age):
                    status = board.board_status(f)
                    self.assertEqual(status["available"], want)
                    self.assertEqual(status["last_check_ok"], ok)  # lets the UI tell "stale" from "failed"


class ServerImport(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.patches = [patch.object(server, "DB", Path(self.td.name) / "runs.db"),
                        patch.object(server, "BOARD_CHECK", Path(self.td.name) / "board_check.json"),
                        patch.dict(os.environ, {"SILICONOS_RUNNER_KEY": KEY.hex(), "SILICONOS_RUNNER_KEY_ID": KID})]
        for p in self.patches:
            p.start()
        self.parents = {l: parent(l) for l in (1, 4)}
        with server.connect() as db:
            for par in self.parents.values():
                db.execute("INSERT INTO runs VALUES (?,?)", (par["id"], json.dumps(par)))

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        self.td.cleanup()  # also proves connections are closed on Windows

    def test_idempotent_child_and_untouched_parent(self):
        env = board.sign(payload(1))
        first = server.import_board_result(RUNS[1][1], env)
        again = server.import_board_result(RUNS[1][1], board.sign(payload(1)))
        self.assertEqual(again["id"], first["id"])
        self.assertTrue(again["already_imported"])
        with server.connect() as db:
            rows = [json.loads(p) for (p,) in db.execute("SELECT payload FROM runs")]
        self.assertEqual(sum(r["evidence"] == "board_measured" for r in rows), 1)
        self.assertIn(self.parents[1], rows)
        with self.assertRaises(LookupError):
            server.import_board_result("00000000-0000-0000-0000-000000000000", env)

    def test_http_signer_to_app(self):
        httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        url = f"http://127.0.0.1:{httpd.server_address[1]}"
        try:
            for lanes in (1, 4):
                self.assertEqual(sign_result.main([str(HW / "results" / RUNS[lanes][0]), "--app", url]), 0)
            import urllib.request
            runs = json.loads(urllib.request.urlopen(url + "/api/runs").read())
            kids = [r for r in runs if r["evidence"] == "board_measured"]
            self.assertEqual(sorted(r["cycles"] for r in kids), [128, 512])
            status = json.loads(urllib.request.urlopen(url + "/api/status").read())
            self.assertFalse(status["board"])
            server.BOARD_CHECK.write_text(json.dumps({"ok": True, "checked_at": datetime.now(timezone.utc).isoformat(),
                                                      "cable_serial": "XFL13U31JOU3A"}))
            status = json.loads(urllib.request.urlopen(url + "/api/status").read())
            self.assertTrue(status["board"])
            req = urllib.request.Request(url + f"/api/runs/{RUNS[1][1]}/board-result",
                                         data=json.dumps({"schema": "nope"}).encode(), method="POST",
                                         headers={"Content-Type": "application/json"})
            with self.assertRaises(urllib.error.HTTPError) as cm:
                urllib.request.urlopen(req)
            self.assertEqual(cm.exception.code, 400)
        finally:
            httpd.shutdown()
            httpd.server_close()


if __name__ == "__main__":
    unittest.main()
