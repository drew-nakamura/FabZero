# Hardware status for the app side (read this first)

**From:** Drew (hardware) + Claude Code. **To:** Christopher (app) + your coding agent. **As of:** 2026-11-14 ~18:20 PT, branch `drew-branch`.
Drew is offline for a few hours. Everything you need from the hardware side is on this branch. Earlier context: `INTEGRATION_QUESTIONS.md` → your `FPGA_INTEGRATION_REPLY.md` → `FPGA_INTEGRATION_RESPONSE.md`.

## 1. Your two handoff ZIPs ran on the KV260 and passed

Source: your `codex/demo-pipeline` `cb92be1`, `data/handoff_exports/`. Import these result folders:

| Your parent run | ZIP | Result folder (on this branch) | Bitstream / manifest used |
|---|---|---|---|
| `6bccf63e-f83a-4e12-88e6-78b20d120b65` (N=8 L1) | `…-n8-l1-handoff.zip` (`112441b7…`) | `hw/matmul_board/results/20261115T011930Z_n8_l1/` | `build/n8_l1/matmul_board_n8_l1.bit` (`63c19180…`), `build/n8_l1/implementation_manifest.json` |
| `3abe54e6-25d2-4eb7-90bf-dd3b39f3a4e9` (N=8 L4) | `…-n8-l4-handoff.zip` (`074dd918…`) | `hw/matmul_board/results/20261115T012007Z_n8_l4/` | `build/n8_l4/matmul_board_n8_l4.bit` (`500cc93b…`), `build/n8_l4/implementation_manifest.json` |

- **Outputs:** all 64 equal your `expected.json`, on the first run, a repeat without reload, and after reset + reload.
- **Cycles:** 512 for L1 and 128 for L4 (equal to your `cycles`).
- **Hashes and parent link:**
  - `input_sha256` uses your raw-byte rule.
  - `source_sha256` is exactly your parent map (`matmul.sv`, `tb.sv`).
  - `parent_run_id` is set.
  - `handoff.zip_sha256` identifies the ZIP.
- **Bitstream:** these runs used the bitstreams built this afternoon from the pinned RTL. That RTL is byte-identical to your ZIPs' `hardware/matmul.sv` and `integration/matmul_axi.sv`; the runner refuses otherwise.

## 2. Clean-room proof (not for import, just evidence the chain is reproducible)

We rebuilt everything from an empty clone, with all old bitstreams, results and our pinned RTL deleted, using **only your ZIPs**:
- `build.py --handoff <zip>` builds from the RTL inside the ZIP. Both builds met timing, with DRC clean and 0 critical warnings, and the same timing and area as before.
- The new bitstreams differ from the committed ones **only in the header build timestamp**. The configuration CRC is identical (`SW_CRC=40a702bc` for L1, `3e00af8b` for L4), so the hardware is the same circuit.
- On the board, both ZIPs passed again on the fresh bitstreams.
- `tests/product_fit_check.py` passed **28/28** for both. It is an independent checker that does not import our runner, and it applies the import rules from your reply (D1, D2, E1).

Those clean-room results stay on Drew's laptop on purpose. Their bitstream hashes (`8ecee10e…` and `4c2783b5…`) are not the committed ones, and the checker correctly fails them against the committed builds. **Import only the two folders in section 1**, which match the committed manifests.

## 3. What your adapter must handle (open on your side)

1. **`null` fields:** `board.board_revision` and `board.kernel_version` are `null`, and `image_identity` is `"none: JTAG boot, no operating system"`. Your D5 says your validator still requires nonempty strings; please relax it. We will not invent values.
2. **Signing:** your adapter re-hashes the `.bit` and the report files against `implementation_manifest.json` (fields `bitstream_sha256`, `report_sha256`, `artifacts_sha256`), maps our fields to your signed envelope, signs with your HMAC key and imports. Your importer/adapter is **not on GitHub yet** (we checked `cb92be1` and `cde8532`). Push it so we can test against your real validator rather than your written rules.
3. **Extra fields you can map or ignore:**
   - `wrapper_sha256` (the `matmul_axi.sv` hash);
   - the `handoff` block (`zip_sha256`, `source_evidence`, `parent_expected_cycles`, `parent_expected_outputs_match`);
   - `repeat_checks.*.outputs` (all 64 values per run);
   - `interface_check.base_address` (`0xA0000000`);
   - `configured_clock_hz` = **99999001** (not 100000000).
4. **Self-check before importing:** run our independent checker on any result folder. It needs no board and no Vivado:
   ```
   python hw/matmul_board/tests/product_fit_check.py hw/matmul_board/results/<run> <your handoff.zip> hw/matmul_board/build/n8_l<LANES>
   ```
   The two section-1 folders give `PRODUCT_FIT: PASS (26/26 checks …)`, plus an INFO line ("bitstream reused … byte-identical to this ZIP's RTL") and the items pending on your side. Builds made with `build.py --handoff` run two extra checks (28/28). We confirmed it fails when a result is checked against the wrong ZIP or a different bitstream.

## 4. How a new run works (for your app or the demo)

| Situation | What happens | Time |
|---|---|---|
| New vectors, N=8, L1 or L4, checked-in RTL (any matrix values) | `run_board.py --handoff <zip>` reuses the existing bitstream because the RTL hash matches | ~1 min on the board |
| RTL changed (for example AI-generated) or N=16 | No bitstream exists; the runner refuses. `build.py --handoff <zip>` would build one (~20 min per configuration), but N=16 and AI RTL on the board are out of scope for the demo (B3/B4) | ~20 min + board |
| Board presence for your E2 indicator | `run_board.py --check` writes `results/board_check.json` (`ok`, `checked_at`, cable, devices) | ~10 s, read-only |

**Your exporter must keep `hardware/*.sv` as LF.** A CRLF checkout changes `matmul.sv`'s hash to `a240756e…`, and the runner then refuses the ZIP. Your `cb92be1` ZIPs are correct (`f81498d1…`).

## 5. Remaining plan to the 12:00 PT deadline

1. **App:** push the importer/adapter; relax the `null` rule; import the two section-1 folders and render them as "board measured".
2. **Both:** one rehearsal: a fresh app run → export → Drew runs `--handoff` (~1 min) → your import.
3. **Both:** record the labelled demo ("Recorded real run", run ID visible).
4. **Shared doc:** `docs/spec/BOARD_RESULT_FILE.md` still shows the old JSON input-hash rule and 100 MHz. The agreed rules are the ones in this file and in your reply. We will update it together; nothing is blocked by it.
