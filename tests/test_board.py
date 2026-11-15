import copy
import hashlib
import io
import json
import tempfile
import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import server
from siliconos import board
from siliconos.board_adapter import adapt_drew_result
from siliconos.engine import DEFAULT, simulate


KEY = "test-only-runner-key-with-at-least-32-bytes"
KEY_ID = "test-runner-v1"


class BoardEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent = simulate(DEFAULT, 1)
        cls.parent.update(id="00000000-0000-0000-0000-000000000101",
                          created_at="2026-11-14T12:00:00+00:00")

    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.db_patch = patch.object(server, "DB", Path(folder.name) / "test.db")
        self.db_patch.start()
        self.addCleanup(self.db_patch.stop)
        self.env_patch = patch.dict("os.environ", {
            board.RUNNER_KEY_ENV: KEY,
            board.RUNNER_KEY_ID_ENV: KEY_ID,
        })
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)
        with server.connect() as db:
            db.execute("INSERT INTO runs VALUES (?,?)", (self.parent["id"], json.dumps(self.parent)))

        outputs = self.parent["outputs"]
        output_hash = board.outputs_sha256(outputs)
        manifest = {
            "schema_version": 1,
            "bitstream_sha256": "a" * 64,
            "vivado_version": "2025.2",
            "target_part": "xck26-sfvc784-2LV-c",
            "top": "matmul_axi",
            "parameters": {"N": 8, "LANES": 1},
            "configured_clock_hz": 100_000_000,
            "timing_met": True,
            "source_sha256": self.parent["source_sha256"],
            "wrapper_sha256": "c" * 64,
            "reports": {
                "timing": "d" * 64,
                "utilization": "e" * 64,
                "drc": "f" * 64,
            },
        }
        unsigned = {
            "schema_version": 1,
            "runner_result_id": str(uuid.uuid4()),
            "parent_run_id": self.parent["id"],
            "evidence": "board_measured",
            "recorded_at": "2026-11-14T12:30:00-08:00",
            "source_sha256": self.parent["source_sha256"],
            "build": {
                "bitstream_sha256": manifest["bitstream_sha256"],
                "vivado_version": manifest["vivado_version"],
                "target_part": manifest["target_part"],
                "top": manifest["top"],
                "parameters": manifest["parameters"],
                "configured_clock_hz": manifest["configured_clock_hz"],
                "timing_met": manifest["timing_met"],
                "implementation_manifest": manifest,
                "implementation_manifest_sha256": hashlib.sha256(board.canonical_bytes(manifest)).hexdigest(),
            },
            "board": {
                "sku": "SK-KV260-G",
                "board_revision": "reported fixture revision",
                "image_identity": "fixture image",
                "kernel_version": "fixture kernel",
                "firmware_identity": "fixture firmware",
                "loader": "fixture loader",
            },
            "interface_check": {
                "identity": board.IDENTITY,
                "compiled_n": 8,
                "compiled_lanes": 1,
            },
            "run": {
                "input_sha256": self.parent["input_sha256"],
                "outputs": outputs,
                "output_sha256": output_hash,
                "cycles": 512,
                "kernel_timing_boundary": "accelerator busy clocks",
                "host_elapsed_ns": None,
                "programming_elapsed_ns": None,
            },
            "lifecycle": {
                "repeat_without_reload": {
                    "outputs": outputs,
                    "output_sha256": output_hash,
                    "cycles": 512,
                },
                "reset_recovery": {
                    "outputs": outputs,
                    "output_sha256": output_hash,
                    "cycles": 512,
                },
            },
        }
        self.payload = board.sign_payload(unsigned, KEY, KEY_ID)

    def resign(self, payload):
        return board.sign_payload(payload, KEY, KEY_ID)

    def post(self, payload=None):
        body = json.dumps(self.payload if payload is None else payload).encode()
        handler = object.__new__(server.Handler)
        handler.path = f"/api/runs/{self.parent['id']}/board-result"
        handler.server = SimpleNamespace(server_port=8000)
        handler.headers = {"Content-Length": str(len(body)), "Origin": "http://127.0.0.1:8000"}
        handler.rfile = io.BytesIO(body)
        replies = []
        handler.reply = lambda status, data: replies.append((status, data))
        handler.do_POST()
        self.assertEqual(len(replies), 1)
        return replies[0]

    def counts(self):
        with server.connect() as db:
            return (
                db.execute("SELECT COUNT(*) FROM runs").fetchone()[0],
                db.execute("SELECT COUNT(*) FROM board_results").fetchone()[0],
                db.execute("SELECT COUNT(*) FROM events").fetchone()[0],
            )

    def test_valid_result_is_authenticated_normalized_and_oracle_checked(self):
        result = board.validate_result(self.parent, self.payload)
        self.assertEqual(result["evidence"], "board_measured")
        self.assertTrue(result["correct"])
        self.assertTrue(result["physical_fpga"])
        self.assertEqual(result["runner_auth"]["key_id"], KEY_ID)
        self.assertEqual(result["cycles"], 512)
        self.assertEqual(result["run"]["outputs"], self.parent["outputs"])
        self.assertEqual(result["lifecycle"]["reset_recovery"]["cycles"], 512)
        self.assertEqual(result["measured_kernel_ns"], 5120.0)
        self.assertIn("runner_payload_sha256", result)

    def test_partner_result_adapter_verifies_saved_artifacts(self):
        root = Path(__file__).resolve().parents[1]
        cases = (
            (1, "20261115T011930Z_n8_l1", "6bccf63e-f83a-4e12-88e6-78b20d120b65"),
            (4, "20261115T012007Z_n8_l4", "3abe54e6-25d2-4eb7-90bf-dd3b39f3a4e9"),
        )
        for lanes, folder, parent_id in cases:
            with self.subTest(lanes=lanes):
                result = root / "hw/matmul_board/results" / folder / "board-result.json"
                build = root / f"hw/matmul_board/build/n8_l{lanes}"
                handoff = root / "data/handoff_exports" / f"siliconos-{parent_id}-n8-l{lanes}-handoff.zip"
                if not all(path.exists() for path in (result, build, handoff)):
                    self.skipTest("Partner's local bitstream, reports, and handoff ZIP are unavailable")
                signed = adapt_drew_result(result, build, handoff)
                self.assertEqual(signed["evidence"], "board_measured")
                self.assertEqual(signed["run"]["cycles"], 512 // lanes)
                self.assertEqual(signed["parent_run_id"], parent_id)
                wrong_build = root / f"hw/matmul_board/build/n8_l{4 if lanes == 1 else 1}"
                with self.assertRaisesRegex(ValueError, "Implementation manifest hash mismatch|Partner artifact verification failed"):
                    adapt_drew_result(result, wrong_build, handoff)

    def test_generated_parent_uses_its_observed_cycle_count(self):
        parent = copy.deepcopy(self.parent)
        parent["evidence"] = "ai_generated_rtl"
        parent["cycles"] = 513
        payload = copy.deepcopy(self.payload)
        payload["run"]["cycles"] = 513
        payload["lifecycle"]["repeat_without_reload"]["cycles"] = 513
        payload["lifecycle"]["reset_recovery"]["cycles"] = 513
        result = board.validate_result(parent, self.resign(payload))
        self.assertEqual(result["cycles"], 513)

    def test_unknown_jtag_board_metadata_remains_null(self):
        payload = copy.deepcopy(self.payload)
        payload["board"]["board_revision"] = None
        payload["board"]["kernel_version"] = None
        payload["board"]["image_identity"] = "none: JTAG boot, no operating system"
        result = board.validate_result(self.parent, self.resign(payload))
        self.assertIsNone(result["board"]["board_revision"])
        self.assertIsNone(result["board"]["kernel_version"])

    def test_authentication_is_required_and_tampering_is_rejected(self):
        unsigned = copy.deepcopy(self.payload)
        unsigned.pop("runner_auth")
        with self.assertRaisesRegex(ValueError, "runner_auth"):
            board.validate_result(self.parent, unsigned)
        tampered = copy.deepcopy(self.payload)
        tampered["run"]["cycles"] = 513
        with self.assertRaisesRegex(ValueError, "authentication failed"):
            board.validate_result(self.parent, tampered)
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(ValueError, "not configured"):
                board.validate_result(self.parent, self.payload)

    def test_mismatched_or_incomplete_physical_evidence_is_rejected(self):
        cases = []
        for path, value in [
            (("parent_run_id",), str(uuid.uuid4())),
            (("evidence",), "rtl_simulation"),
            (("source_sha256", "matmul.sv"), "0" * 64),
            (("build", "top"), "other"),
            (("build", "parameters", "LANES"), 4),
            (("build", "timing_met"), False),
            (("build", "implementation_manifest_sha256"), "0" * 64),
            (("build", "implementation_manifest", "reports", "timing"), "0" * 64),
            (("board", "sku"), "other"),
            (("interface_check", "identity"), 0),
            (("interface_check", "compiled_lanes"), 4),
            (("run", "input_sha256"), "0" * 64),
            (("run", "outputs"), [0] * 64),
            (("run", "output_sha256"), "0" * 64),
            (("run", "cycles"), 513),
            (("lifecycle", "repeat_without_reload", "cycles"), 513),
            (("lifecycle", "reset_recovery", "outputs"), [0] * 64),
        ]:
            payload = copy.deepcopy(self.payload)
            target = payload
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            cases.append((".".join(path), self.resign(payload)))
        payload = copy.deepcopy(self.payload)
        payload["unexpected"] = True
        cases.append(("unexpected", self.resign(payload)))
        for name, payload in cases:
            with self.subTest(name=name), self.assertRaises(ValueError):
                board.validate_result(self.parent, payload)

    def test_canonical_hash_encodings_are_stable(self):
        self.assertEqual(
            board.outputs_sha256([1, -2, 3]),
            "291bbc895d1412460556618bc33cfcc323cac88cbfae4a2062ccfbd2afb51ec7",
        )
        self.assertEqual(board.payload_sha256({"b": 2, "a": 1}),
                         board.payload_sha256({"a": 1, "b": 2}))

    def test_endpoint_persists_separate_child_and_retries_idempotently(self):
        status, result = self.post()
        self.assertEqual(status, 200, result)
        self.assertNotEqual(result["id"], self.parent["id"])
        self.assertEqual(result["parent_run_id"], self.parent["id"])
        self.assertEqual(self.counts(), (2, 1, 1))
        status, replay = self.post()
        self.assertEqual(status, 200, replay)
        self.assertEqual(replay["id"], result["id"])
        self.assertEqual(self.counts(), (2, 1, 1))

    def test_duplicate_runner_id_cannot_describe_different_evidence(self):
        self.assertEqual(self.post()[0], 200)
        changed = copy.deepcopy(self.payload)
        changed["recorded_at"] = "2026-11-14T12:31:00-08:00"
        status, result = self.post(self.resign(changed))
        self.assertEqual(status, 400, result)
        self.assertIn("already used", result["error"])
        self.assertEqual(self.counts(), (2, 1, 1))

    def test_missing_parent_and_atomic_failure_create_no_child(self):
        original = self.parent["id"]
        self.parent["id"] = "00000000-0000-0000-0000-000000000999"
        try:
            status, result = self.post()
        finally:
            self.parent["id"] = original
        self.assertEqual(status, 404, result)
        self.assertEqual(self.counts(), (1, 0, 0))

        with server.connect() as db:
            db.execute("CREATE TRIGGER fail_board_event BEFORE INSERT ON events BEGIN SELECT RAISE(ABORT, 'test rollback'); END")
        status, result = self.post()
        self.assertEqual(status, 502, result)
        self.assertEqual(self.counts(), (1, 0, 0))


if __name__ == "__main__":
    unittest.main()
