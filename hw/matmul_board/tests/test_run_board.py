#!/usr/bin/env python3
"""Offline checks for the board runner (no board needed).

  python hw/matmul_board/tests/test_run_board.py

1. Python-only: canned transcripts (good, wrong output, wrong cycles, timeout,
   bad identity/LANES, truncated, xsdb error, reset not cleared, unparseable)
   go through run_board.py --replay; checks status, evidence label, hashes and
   the atomic result folder.
2. xsdb mock (skipped if xsdb is not installed): runs the real run_matmul.tcl
   in xsdb against tests/mock_board.tcl, a register-level model of matmul_axi,
   with injected faults, then judges the transcript with run_board.py.
Nothing here is board evidence; replay results are labelled replay_test_not_board.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOARD = HERE.parent
sys.path.insert(0, str(BOARD))
import run_board  # noqa: E402

XSDB = Path(r"C:/AMDDesignTools/2025.2/Vivado/bin/xsdb.bat")
RTL_SHA = {"matmul.sv": "f81498d1fdb9a73a32e7f70a5d55c09b6198d2f03f00ab27d9099a63d82f418c",
           "matmul_axi.sv": "26d5eca5ea16bf81336cece4f9a76617cfaf5444cc4b92a734a656cff4dc080c"}
# Stub with the same shape as a real psu_init.tcl: a global data table read
# through `variable` inside the proc. Fails if run_matmul.tcl sources it in proc scope.
PSU_STUB = """set psu_ps_pl_reset_config_data {mock_reset}
proc init_ps {data} { foreach cmd [split $data ";"] { if {[string trim $cmd] ne ""} { uplevel #0 $cmd } } }
proc psu_init {} {}
proc psu_ps_pl_isolation_removal {} {}
proc psu_ps_pl_reset_config {} { variable psu_ps_pl_reset_config_data; init_ps $psu_ps_pl_reset_config_data }
"""


def fake_build(root, lanes, timing_met=True):
    d = Path(root) / f"n8_l{lanes}"
    d.mkdir(parents=True)
    (d / "addresses.tcl").write_text("set MATMUL_BASE 0xA0000000\nset MATMUL_RANGE 0x00001000\n")
    (d / "psu_init.tcl").write_text(PSU_STUB)
    (d / f"matmul_board_n8_l{lanes}.bit").write_bytes(b"not a real bitstream")
    m = {"parameters": {"N": 8, "LANES": lanes}, "rtl": {"sha256": RTL_SHA},
         "bitstream_sha256": "0" * 64, "vivado_version": "2025.2",
         "target_part": "xck26-sfvc784-2LV-c", "board_part": "xilinx.com:kv260_som:part0:1.4",
         "logical_top": "matmul_axi", "board_top": "matmul_board_top",
         "configured_clock_hz": 99999001, "timing": {"timing_met": timing_met}, "drc_clean": True,
         "address_map": {"base_address": "0xA0000000"}, "artifacts_sha256": {}}
    (d / "implementation_manifest.json").write_text(json.dumps(m))
    return d


def transcript(lanes=1, outputs=None, cycles=None, ident=0x53494C01, tlanes=None, status_idle=0,
               reset_status=0, timeout_job=None, truncate=False, error=None, extra=""):
    exp = [i - 32 for i in range(64)]
    outs = outputs if outputs is not None else exp
    cyc = cycles if cycles is not None else 512 // lanes
    lines = ["MM BEGIN n=8 base=0xA0000000", "MM CABLE XFL13U31JOU3", "MM PROGRAM_NS 1500000000",
             f"MM ID {ident}", "MM N 8", f"MM LANES {tlanes if tlanes is not None else lanes}",
             f"MM STATUS_IDLE {status_idle}", "MM SCRATCH 5 0"]
    for label in ("first", "repeat", "reset_reload"):
        if label == "reset_reload":
            lines.append(f"MM RESET status={reset_status} cycles_lo=0 cycles_hi=0")
        if label == timeout_job:
            lines.append(f"MM JOB {label} status=1 polls=2000 timeout=1")
            continue
        lines.append(f"MM JOB {label} status=2 polls=0 timeout=0 cycles_lo={cyc} cycles_hi=0 host_ns=4000000000")
        lines.append(f"MM OUT {label} " + " ".join(map(str, outs)))
    if error:
        lines.append(f"MM ERROR {error}")
    lines.append(extra)
    if not truncate:
        lines.append("MM END")
    return "xsdb noise line\n" + "\n".join(lines) + "\n"


class RunnerReplay(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.root = Path(self.td.name)

    def tearDown(self):
        self.td.cleanup()

    def replay(self, text, lanes=1, timing_met=True):
        b = fake_build(self.root / f"build{len(list(self.root.iterdir()))}", lanes, timing_met)
        tp = self.root / f"t{len(list(self.root.iterdir()))}.txt"
        tp.write_text(text)
        out = self.root / "results"
        rc = run_board.main(["--lanes", str(lanes), "--replay", str(tp), "--results-dir", str(out),
                             "--build-dir", str(b)])
        runs = sorted(p for p in out.iterdir() if not p.name.startswith(".tmp_"))
        self.assertFalse([p for p in out.iterdir() if p.name.startswith(".tmp_")], "temp folder left")
        r = runs[-1]
        res = json.loads((r / "board-result.json").read_text())
        self.assertEqual((r / "xsdb.log").read_text(), text)
        return rc, res, r

    def test_good_one_lane_passes_with_correct_hashes(self):
        rc, res, r = self.replay(transcript())
        self.assertEqual((rc, res["status"], res["failure_reason"]), (0, "pass", None))
        self.assertEqual(res["evidence"], "replay_test_not_board")
        self.assertTrue(r.name.endswith("_n8_l1_replay"))
        inputs = json.loads((r / "inputs.json").read_bytes())
        # Agreed rule (app D1): SHA256 of the raw INT8 bytes of A then B.
        self.assertEqual(res["run"]["input_sha256"],
                         hashlib.sha256(bytes(x & 255 for x in inputs["A"] + inputs["B"])).hexdigest())
        self.assertEqual(inputs["B"], [i - 32 for i in range(64)])
        self.assertEqual(res["run"]["outputs"], [i - 32 for i in range(64)])
        self.assertEqual(res["run"]["output_sha256"], hashlib.sha256(
            json.dumps([i - 32 for i in range(64)], separators=(",", ":")).encode()).hexdigest())
        self.assertEqual(res["run"]["cycles"], 512)
        self.assertEqual(res["interface_check"]["identity"], 1397312513)
        self.assertTrue(res["interface_check"]["scratch_register_ok"])
        self.assertEqual(res["repeat_checks"]["reset_reload_rerun"],
                         {"outputs_match": True, "cycles": 512, "outputs": [i - 32 for i in range(64)]})
        self.assertIsNone(res["parent_run_id"])
        self.assertIsNone(res["handoff"])
        self.assertEqual(res["board"]["jtag_cable_serial"], "XFL13U31JOU3")
        for key in ("schema_version", "runner_result_id", "parent_run_id", "recorded_at", "source_sha256",
                    "build", "board", "interface_check", "run", "repeat_checks", "workload_id"):
            self.assertIn(key, res)

    def test_good_four_lane_needs_128_cycles(self):
        rc, res, _ = self.replay(transcript(lanes=4), lanes=4)
        self.assertEqual(res["status"], "pass")
        rc, res, _ = self.replay(transcript(lanes=4, cycles=512), lanes=4)
        self.assertEqual(res["status"], "fail")
        self.assertIn("cycles 512 != expected 128", res["failure_reason"])

    def assertFails(self, text, needle, lanes=1, **kw):
        rc, res, _ = self.replay(text, lanes=lanes, **kw)
        self.assertEqual((rc, res["status"]), (1, "fail"))
        self.assertIsNone(res["evidence"], "a failed run must not carry an evidence claim")
        self.assertIn(needle, res["failure_reason"])
        return res

    def test_wrong_output_fails(self):
        bad = [i - 32 for i in range(64)]
        bad[17] += 1
        res = self.assertFails(transcript(outputs=bad), "output mismatch")
        self.assertFalse(res["run"]["expected_outputs_match"])
        self.assertEqual(res["run"]["outputs"][17], bad[17])

    def test_wrong_cycles_fails(self):
        self.assertFails(transcript(cycles=513), "cycles 513 != expected 512")

    def test_timeout_fails(self):
        self.assertFails(transcript(timeout_job="repeat"), "repeat: done timeout")

    def test_bad_identity_and_lanes_fail(self):
        self.assertFails(transcript(ident=0), "identity 0")
        self.assertFails(transcript(tlanes=4), "compiled LANES 4 != 1")

    def test_truncated_transcript_fails(self):
        self.assertFails(transcript(truncate=True), "transcript incomplete")

    def test_xsdb_error_fails(self):
        self.assertFails(transcript(error="Memory read error at 0xA0000014"), "xsdb error")

    def test_reset_not_cleared_fails(self):
        self.assertFails(transcript(reset_status=2), "status after PL reset 2")

    def test_busy_before_start_fails(self):
        self.assertFails(transcript(status_idle=1), "not idle")

    def test_unparseable_line_fails(self):
        self.assertFails(transcript(extra="MM ID notanumber"), "unparseable line")

    def test_manifest_without_timing_fails(self):
        self.assertFails(transcript(), "timing met", timing_met=False)

    def test_replay_cannot_write_live_results(self):
        b = fake_build(self.root / "b", 1)
        tp = self.root / "t.txt"
        tp.write_text(transcript())
        with self.assertRaises(SystemExit):
            run_board.main(["--lanes", "1", "--replay", str(tp), "--results-dir",
                            str(run_board.LIVE_RESULTS / "x"), "--build-dir", str(b)])

    def test_reference_model_and_self_check(self):
        a = [-128] * 64
        self.assertEqual(run_board.reference_matmul(a, a, 8), [131072] * 64)
        a, b = run_board.identity_ramp(8)
        self.assertEqual(run_board.reference_matmul(a, b, 8), [i - 32 for i in range(64)])
        self.assertTrue(run_board.comparator_self_check([i - 32 for i in range(64)]))


def vectors():
    a = [((i * 37 + 11) % 256) - 128 for i in range(64)]
    b = [((i * 53 + 7) % 256) - 128 for i in range(64)]
    return a, b


def make_zip(path, lanes, run_id="11111111-2222-3333-4444-555555555555", crlf=False, tamper=False,
             bad_expected=False):
    """A handoff ZIP in the exact layout of the app's siliconos/handoff.py (schema_version 1)."""
    import zipfile
    a, b = vectors()
    outs = run_board.reference_matmul(a, b, 8)
    if bad_expected:
        outs = list(outs)
        outs[3] += 1
    mm = (BOARD / "rtl" / "matmul.sv").read_bytes()
    if crlf:
        mm = mm.replace(b"\n", b"\r\n")
    files = {
        "hardware/matmul.sv": mm,
        "hardware/tb.sv": b"// testbench snapshot\nmodule tb; endmodule\n",
        "inputs.hex": ("\n".join(f"{x & 255:02x}" for x in a + b) + "\n").encode(),
        "expected.json": json.dumps({"inputs": {"a": a, "b": b}, "outputs": outs, "cycles": 512 // lanes,
                                     "parameters": {"N": 8, "LANES": lanes}}, indent=2).encode(),
        "integration/matmul_axi.sv": (BOARD / "rtl" / "matmul_axi.sv").read_bytes(),
        "integration/matmul.sv": mm,
        "README.md": b"# Verified kernel handoff\n",
    }
    manifest = {"schema_version": 1, "run_id": run_id, "source_evidence": "rtl_simulation",
                "original_target": "kv260", "requested_target": "kv260", "board_sku": "SK-KV260-G",
                "reported_vivado": "2025.2", "parameters": {"N": 8, "LANES": lanes}, "physical_fpga": False,
                "integration_status": "unverified for this run",
                "files_sha256": {k: hashlib.sha256(v).hexdigest() for k, v in files.items()}}
    if tamper:
        files["hardware/tb.sv"] += b"// edited after export\n"
    files["manifest.json"] = json.dumps(manifest, indent=2).encode()
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for k, v in files.items():
            z.writestr(k, v)
    return a, b, outs


class Handoff(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.root = Path(self.td.name)

    def tearDown(self):
        self.td.cleanup()

    def run_handoff(self, lanes=1, outputs=None, cli_lanes=None, **zipkw):
        zp = self.root / f"h{len(list(self.root.iterdir()))}.zip"
        a, b, outs = make_zip(zp, lanes, **zipkw)
        bdir = fake_build(self.root / f"b{len(list(self.root.iterdir()))}", lanes)
        tp = self.root / f"t{len(list(self.root.iterdir()))}.txt"
        tp.write_text(transcript(lanes=lanes, outputs=outputs if outputs is not None
                                 else run_board.reference_matmul(a, b, 8)))
        out = self.root / "results"
        args = ["--handoff", str(zp), "--replay", str(tp), "--results-dir", str(out), "--build-dir", str(bdir)]
        if cli_lanes:
            args += ["--lanes", str(cli_lanes)]
        rc = run_board.main(args)
        run = sorted(p for p in out.iterdir() if not p.name.startswith("."))[-1]
        return rc, json.loads((run / "board-result.json").read_text()), a, b, zp, run

    def test_handoff_pass_links_parent_and_uses_app_hash_rules(self):
        for lanes in (1, 4):
            with self.subTest(lanes=lanes):
                rc, res, a, b, zp, run = self.run_handoff(lanes)
                self.assertEqual((rc, res["status"]), (0, "pass"), res["failure_reason"])
                self.assertEqual(res["parent_run_id"], "11111111-2222-3333-4444-555555555555")
                self.assertEqual(res["workload_id"], "siliconos-run-11111111-2222-3333-4444-555555555555")
                self.assertEqual(res["run"]["input_sha256"],
                                 hashlib.sha256(bytes(x & 255 for x in a + b)).hexdigest())
                self.assertEqual(res["source_sha256"], {
                    "matmul.sv": RTL_SHA["matmul.sv"],
                    "tb.sv": hashlib.sha256(b"// testbench snapshot\nmodule tb; endmodule\n").hexdigest()})
                self.assertEqual(res["wrapper_sha256"], RTL_SHA["matmul_axi.sv"])
                self.assertEqual(res["handoff"]["zip_sha256"], hashlib.sha256(zp.read_bytes()).hexdigest())
                self.assertTrue(res["handoff"]["parent_expected_outputs_match"])
                self.assertEqual(res["run"]["cycles"], 512 // lanes)
                self.assertEqual(res["repeat_checks"]["reset_reload_rerun"]["outputs"], res["run"]["outputs"])
                self.assertEqual(json.loads((run / "inputs.json").read_text()), {"A": a, "B": b})

    def test_wrong_board_output_fails_against_parent(self):
        a, b = vectors()
        bad = run_board.reference_matmul(a, b, 8)
        bad[9] += 1
        rc, res, *_ = self.run_handoff(1, outputs=bad)
        self.assertEqual((rc, res["status"]), (1, "fail"))
        self.assertIsNone(res["evidence"])
        self.assertIn("differ from the parent run", res["failure_reason"])
        self.assertEqual(res["parent_run_id"], "11111111-2222-3333-4444-555555555555")

    def test_refusals_before_loading(self):
        for kw, needle in [({"tamper": True}, "does not match its manifest hash"),
                           ({"crlf": True}, "line endings"),
                           ({"bad_expected": True}, "disagree with the independent reference"),
                           ({"cli_lanes": 4}, "differs from the ZIP")]:
            with self.subTest(**kw):
                with self.assertRaises(SystemExit) as cm:
                    self.run_handoff(1, **kw)
                self.assertIn(needle, str(cm.exception))

    def test_check_board_parsing(self):
        from unittest import mock
        good = ("CHECK CABLE XFL13U31JOU3A\nCHECK DEVICE 1  Xilinx X-MLCC-01 XFL13U31JOU3A\n"
                "CHECK DEVICE 2  xck26 (idcode 04724093 irlen 12 fpga)\n"
                "CHECK DEVICE 3  arm_dap (idcode 5ba00477 irlen 4)\nCHECK END\n")
        for text, ok in [(good, True), ("CHECK CABLE \nCHECK END\n", False),
                         ("CHECK ERROR connect failed: no hw_server\nCHECK END\n", False)]:
            with mock.patch.object(run_board.subprocess, "run",
                                   return_value=subprocess.CompletedProcess([], 0, text, "")):
                rec = run_board.check_board(self.root / "res")
            self.assertEqual(rec["ok"], ok, rec)
            saved = json.loads((self.root / "res" / "board_check.json").read_text())
            self.assertEqual(saved["ok"], ok)
            if ok:
                self.assertEqual(rec["cable_serial"], "XFL13U31JOU3A")
            else:
                self.assertTrue(rec["reason"])


@unittest.skipUnless(XSDB.exists(), "xsdb not installed")
class XsdbMock(unittest.TestCase):
    """Real run_matmul.tcl in xsdb against the register model in mock_board.tcl."""

    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        cls.root = Path(cls.td.name)
        a, b = run_board.identity_ramp(8)
        cls.inputs = cls.root / "inputs.tcl"
        cls.inputs.write_text(f"set A {{{' '.join(map(str, a))}}}\nset B {{{' '.join(map(str, b))}}}\n")

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def run_mock(self, fault, lanes=1):
        b = fake_build(self.root / f"{fault}_{lanes}", lanes)
        cmd = [str(XSDB), str(HERE / "mock_board.tcl"), fault, str(lanes),
               (b / f"matmul_board_n8_l{lanes}.bit").as_posix(), (b / "psu_init.tcl").as_posix(),
               (b / "addresses.tcl").as_posix(), self.inputs.as_posix(), "8"]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=self.root)
        text = p.stdout + p.stderr
        tp = self.root / f"{fault}_{lanes}.txt"
        tp.write_text(text)
        out = self.root / "results"
        rc = run_board.main(["--lanes", str(lanes), "--replay", str(tp), "--results-dir", str(out),
                             "--build-dir", str(b)])
        run = sorted(out.glob(f"*_n8_l{lanes}_replay"))[-1]
        res = json.loads((run / "board-result.json").read_text())
        return rc, res, text

    def test_mock_good_one_lane(self):
        rc, res, text = self.run_mock("none", 1)
        self.assertEqual(res["status"], "pass", f"{res['failure_reason']}\n{text}")
        self.assertEqual(res["run"]["cycles"], 512)
        self.assertEqual(res["board"]["jtag_cable_serial"], "MOCK0000")

    def test_mock_good_four_lane(self):
        rc, res, text = self.run_mock("none", 4)
        self.assertEqual(res["status"], "pass", f"{res['failure_reason']}\n{text}")
        self.assertEqual(res["run"]["cycles"], 128)

    def test_mock_faults_are_caught(self):
        for fault, needle in [("result", "output mismatch"), ("cycles", "cycles 513"),
                              ("hang", "done timeout"), ("identity", "identity 0"),
                              ("noreset", "status after PL reset"), ("lanes", "compiled LANES 3")]:
            with self.subTest(fault=fault):
                rc, res, text = self.run_mock(fault, 1)
                self.assertEqual(res["status"], "fail", text)
                self.assertIsNone(res["evidence"])
                self.assertIn(needle, res["failure_reason"], text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
