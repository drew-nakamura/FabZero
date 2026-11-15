"""Live-pipeline FPGA stage: Vivado evidence, report/result access, and app-started board jobs.

Board jobs run with a stand-in for run_board.py (no KV260 is touched); signing, the
file re-verification in sign_result.py and the import checks are the real code.
"""
import io
import json
import os
import secrets
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import server
from siliconos import fpga
from test_board_import import RUNS, parent

ROOT = Path(__file__).resolve().parents[1]
KEY, KID = secrets.token_bytes(32), "test-key"


def source_run(lanes):
    """A stored simulation run of the checked-in RTL, as the app saves it."""
    run = parent(lanes)
    run["source_files"] = {n: (ROOT / "hardware" / n).read_text(encoding="utf-8") for n in ("matmul.sv", "tb.sv")}
    return run


class FakeProc:
    def __init__(self, lines, code):
        self.stdout = io.StringIO("".join(line + "\n" for line in lines))
        self.code = code

    def wait(self, timeout=None):
        return self.code


def wait_job(job_id, timeout=60):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        job = fpga.get_job(job_id)
        if job["status"] != "running":
            return job
        time.sleep(0.05)
    raise AssertionError("board job did not finish")


class BuildEvidence(unittest.TestCase):
    def test_committed_builds_are_verified_and_bound_to_the_app_rtl(self):
        one, four = fpga.build_evidence(1), fpga.build_evidence(4)
        for b in (one, four):
            self.assertTrue(b["rtl_matches_app"] and b["bitstream_verified"] and b["summary_verified"])
            self.assertTrue(b["timing"]["met"] and b["drc_clean"])
            self.assertTrue(all(r["verified"] for r in b["reports"]))
            self.assertEqual(b["timing"]["failing"], 0)
        self.assertEqual((one["area"]["Total LUTs"], four["area"]["Total LUTs"]), (354, 3612))
        self.assertEqual((one["timing"]["WNS_ns"], four["timing"]["WNS_ns"]), (4.757, 3.885))
        self.assertEqual(one["bitstream_sha256"][:8], "63c19180")
        self.assertGreater(one["build_minutes"], 1)
        with self.assertRaises(ValueError):
            fpga.build_evidence(2)

    def test_reports_are_allowlisted_and_hash_checked(self):
        self.assertIn(b"Timing", fpga.report_text(1, "timing_summary.rpt"))
        for name in ("../implementation_manifest.json", "nope.rpt"):
            with self.assertRaises(LookupError):
                fpga.report_text(1, name)
        with tempfile.TemporaryDirectory() as td:
            import shutil
            shutil.copytree(fpga.BUILD / "n8_l1", Path(td) / "n8_l1", ignore=shutil.ignore_patterns("proj", "rtl"))
            rpt = Path(td) / "n8_l1" / "reports" / "power.rpt"
            rpt.write_bytes(rpt.read_bytes() + b"x")
            with patch.object(fpga, "BUILD", Path(td)), self.assertRaisesRegex(ValueError, "no longer matches"):
                fpga.report_text(1, "power.rpt")

    def test_result_files_only_from_run_folders(self):
        body, mime = fpga.result_file(RUNS[1][0], "xsdb.log")
        self.assertIn(b"MM ", body)
        self.assertTrue(mime.startswith("text/plain"))
        for folder, name in ((RUNS[1][0], "inputs.json"), ("..", "xsdb.log"), ("..\\build", "xsdb.log"),
                             ("20991231T000000Z_n8_l1", "xsdb.log")):
            with self.assertRaises(LookupError):
                fpga.result_file(folder, name)
        runner_id = json.loads((fpga.RESULTS / RUNS[4][0] / "board-result.json").read_text())["runner_result_id"]
        self.assertEqual(fpga.find_result_folder(runner_id), RUNS[4][0])

    def test_handoff_contents_lists_hashed_files(self):
        h = fpga.handoff_contents(source_run(1))
        names = {f["name"] for f in h["files"]}
        self.assertTrue({"hardware/matmul.sv", "hardware/tb.sv", "expected.json", "manifest.json"} <= names)
        self.assertEqual(next(f for f in h["files"] if f["name"] == "hardware/matmul.sv")["sha256"][:8], "f81498d1")


class BoardJobs(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.patches = [patch.object(server, "DB", Path(self.td.name) / "runs.db"),
                        patch.object(fpga, "HANDOFFS", Path(self.td.name) / "handoffs"),
                        patch.dict(os.environ, {"SILICONOS_RUNNER_KEY": KEY.hex(), "SILICONOS_RUNNER_KEY_ID": KID})]
        for p in self.patches:
            p.start()
        self.run1 = source_run(1)
        with server.connect() as db:
            db.execute("INSERT INTO runs VALUES (?,?)", (self.run1["id"], json.dumps(self.run1)))
        fpga.JOBS.clear()

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        self.td.cleanup()

    def test_only_checked_in_8x8_simulations_can_run(self):
        for change, needle in (({"evidence": "ai_generated_rtl"}, "AI-generated RTL has no bitstream"),
                               ({"spec": {**self.run1["spec"], "size": 16}}, "8x8"),
                               ({"correct": False}, "verified simulation")):
            with self.subTest(needle=needle), self.assertRaisesRegex(ValueError, needle):
                fpga.start_board_run({**self.run1, **change}, server.import_board_result)

    def test_board_job_signs_and_imports_a_passing_run(self):
        folder = RUNS[1][0]
        lines = ["> xsdb run_matmul.tcl ...", f"MATMUL_BOARD_RESULT: PASS {fpga.RESULTS / folder}"]
        with patch("siliconos.fpga.subprocess.Popen", return_value=FakeProc(lines, 0)) as popen:
            job = fpga.start_board_run(self.run1, server.import_board_result)
            with self.assertRaisesRegex(ValueError, "already active"):
                fpga.start_board_run(self.run1, server.import_board_result)
            job = wait_job(job["id"])
        self.assertEqual(job["status"], "done", job)
        cmd = popen.call_args.args[0]
        self.assertEqual(cmd[-2], "--handoff")
        self.assertTrue(Path(cmd[-1]).name.endswith("-handoff.zip"))
        self.assertEqual(job["result_folder"], folder)
        self.assertEqual(len(job["zip_sha256"]), 64)
        with server.connect() as db:
            child = json.loads(db.execute("SELECT payload FROM runs WHERE id=?", (job["child_id"],)).fetchone()[0])
        self.assertEqual((child["evidence"], child["parent_run_id"], child["cycles"]), ("board_measured", self.run1["id"], 512))
        self.assertEqual(child["runner_result_folder"], folder)
        self.assertEqual(child["board_import"]["key_id"], KID)

    def test_failed_board_run_is_reported_and_never_imported(self):
        lines = [f"MATMUL_BOARD_RESULT: FAIL (outputs mismatch) {fpga.RESULTS / '20261115T000000Z_n8_l1'}"]
        with patch("siliconos.fpga.subprocess.Popen", return_value=FakeProc(lines, 1)):
            job = wait_job(fpga.start_board_run(self.run1, server.import_board_result)["id"])
        self.assertEqual(job["status"], "failed")
        self.assertIn("outputs mismatch", job["error"])
        with server.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM runs").fetchone()[0], 1)

    def test_http_routes(self):
        def get(path):
            h = object.__new__(server.Handler); h.path = path
            replies, files = [], []
            h.reply = lambda code, body: replies.append((code, body))
            h.send_file = lambda body, mime: files.append((body, mime))
            h.do_GET()
            return replies[0] if replies else (200, files[0])
        code, body = get("/api/fpga/builds")
        self.assertEqual((code, [b["lanes"] for b in body["builds"]]), (200, [1, 4]))
        self.assertEqual(get("/api/fpga/builds/4/reports/utilization.rpt")[0], 200)
        self.assertEqual(get("/api/fpga/builds/4/reports/missing.rpt")[0], 404)
        self.assertEqual(get("/api/fpga/builds/2/reports/utilization.rpt")[0], 404)
        self.assertEqual(get(f"/api/board/results/{RUNS[1][0]}/board-result.json")[0], 200)
        self.assertEqual(get("/api/board/results/..%2Fbuild/xsdb.log")[0], 404)
        code, body = get(f"/api/runs/{self.run1['id']}/handoff.json")
        self.assertEqual(code, 200)
        self.assertEqual(get("/api/board/jobs/00000000-0000-0000-0000-000000000000")[0], 404)
        with patch.dict(os.environ, {"GROQ_API_KEY": "gsk_sentinel_never_shown", "GROQ_MODEL": "openai/gpt-oss-20b"}):
            code, status = get("/api/status")
        self.assertNotIn("asic_synthesis", status)
        self.assertEqual((status["ai"], status["ai_details"]["model"], status["ai_details"]["missing"]),
                         (True, "openai/gpt-oss-20b", []))
        self.assertNotIn("gsk_sentinel_never_shown", json.dumps(status))

    def test_board_run_route_refuses_unknown_and_unsupported_runs(self):
        def post(path):
            h = object.__new__(server.Handler); h.path = path
            h.server = SimpleNamespace(server_port=8000)
            h.headers = {"Content-Length": "2"}; h.rfile = io.BytesIO(b"{}")
            replies = []; h.reply = lambda code, body: replies.append((code, body))
            h.do_POST(); return replies[0]
        self.assertEqual(post("/api/runs/00000000-0000-0000-0000-000000000000/board-run")[0], 404)
        ai_run = {**self.run1, "id": "11111111-1111-1111-1111-111111111111", "evidence": "ai_generated_rtl"}
        with server.connect() as db:
            db.execute("INSERT INTO runs VALUES (?,?)", (ai_run["id"], json.dumps(ai_run)))
        code, body = post(f"/api/runs/{ai_run['id']}/board-run")
        self.assertEqual(code, 400)
        self.assertIn("no bitstream", body["error"])


if __name__ == "__main__":
    unittest.main()
