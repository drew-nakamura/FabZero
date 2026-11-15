# Hardware response to the app integration reply

**From:** Drew (hardware) + Claude Code. **To:** Christopher (app) + your coding agent. **Date:** 2026-11-14.
**Replies to:** your `FPGA_INTEGRATION_REPLY.md`. We accept your changes. This file confirms the decisions, answers your open items, and lists exactly what we need from you so we can run your vectors on the board before the Sunday 12:00 PT cutoff.

## 1. Decisions confirmed (Drew)

- **Owners (F2):** Drew is hardware merge owner; Christopher is app integration owner.
- **Signing adapter:** **your side** writes the trusted adapter. It reads our raw result folder, verifies the files, maps them to your signed envelope and imports them. You own the schema, the validator and the HMAC key, so the key never touches our scripts.
- **First end-to-end path:** manual, as you proposed. Your ZIP → our runner on the board → our raw result folder → your adapter signs → app import. Automate later, only if time allows.
- **We accept all your "Change" rows:** B1, B2, D1, D2 and D5, plus the stricter C1 cache key and every "Agree" row.

## 2. Answers to your open items (from the real build, not assumed)

| Item | Value | Where it comes from |
|---|---|---|
| Vivado part | `xck26-sfvc784-2LV-c`, board part `xilinx.com:kv260_som:part0:1.4`, Vivado 2025.2 | `build/n8_l*/implementation_manifest.json` |
| MMIO address | base `0xA0000000`, range `0x1000` | Read back from the block design by `build.tcl` (`build/n8_l*/addresses.tcl`) |
| Clock | `pl_clk0` = **99,999,001 Hz** (PS PLL); timing constraint 10.000 ns | `implementation_manifest.json` → `configured_clock_hz` |
| Your branch's RTL vs our bitstreams | **Byte-identical.** On `codex/demo-pipeline` at `9677e03`, `hardware/matmul.sv` has SHA256 `f81498d1…82f418c` and `hardware/matmul_axi.sv` has `26d5eca5…dc080c`. Both match our build manifests. | We checked your pushed commit |

## 3. What we will change on the hardware side (starting now)

The runner (`hw/matmul_board/run_board.py`) gets a `--handoff <your ZIP>` mode. It reads **your current ZIP format unchanged**, so you don't need to add `inputs.json`:

1. **Verify the ZIP.** Check every entry against `manifest.json` → `files_sha256`. Require `parameters.N == 8` and `LANES` in {1, 4}. Take `parent_run_id = manifest.run_id`.
2. **Read the vectors** from `expected.json` → `inputs.a` / `inputs.b`, and the expected outputs and cycles from the same file.
3. **Bind the source to the bitstream.**
   - The SHA256 of `hardware/matmul.sv` in the ZIP must equal the `matmul.sv` hash in our build manifest.
   - `integration/matmul_axi.sv` must equal our wrapper hash.
   - If either differs, the runner refuses to load the board.
   - This picks the immutable artifact `build/n8_l<LANES>/` (manifest + bitstream).
4. **Run the board** exactly as before: interface check, first run, repeat without reload, reset → reload → rerun.
5. **Write the raw result folder** with these changes:
   - `parent_run_id` is filled in.
   - `input_sha256` uses **your rule**: SHA256 of the 128 raw bytes `bytes(x & 255 for x in A+B)`.
   - `source_sha256` is **your parent's map copied from the ZIP** (`matmul.sv`, `tb.sv`).
   - A separate `wrapper_sha256` holds `matmul_axi.sv`.
   - `handoff_zip_sha256` is added.
   - All outputs of all three runs are included.
   - Our own checks against both your `expected.json` and our independent reference model.
6. **Add `run_board.py --check`:** read-only JTAG detection (cable, `xck26` device, debug targets). It writes `results/board_check.json` with a timestamp and loads nothing.

Unchanged: one board run at a time, `evidence: null` on any failure, nothing ever overwritten, and the bitstream / `psu_init.tcl` / address-map hashes verified against the manifest before loading.

## 4. What we need from you (blocking, in this order)

1. **One real handoff ZIP for each lane count:** an accepted, checked-in-RTL run at N=8 LANES=1, and one at N=8 LANES=4. Two ZIPs, exported by your app as they are.
2. **Fix line endings before exporting. We reproduced this problem.** Your export hashes the text of `hardware/matmul.sv` as read from disk. We ran **your own `siliconos/handoff.py` from `9677e03`** on a Windows checkout with `core.autocrlf=true`:
   - Your ZIP then records `matmul.sv` = `a240756e6289c6506e0d7d84ce952d6915b8cc409b93b2cc1cb38938f1269d5b` (CRLF).
   - Our bitstream was built from `f81498d1fdb9a73a32e7f70a5d55c09b6198d2f03f00ab27d9099a63d82f418c` (LF). Our runner correctly **refuses** that ZIP.
   - With LF line endings, your ZIPs load and bind for both lane counts.

   **Fix:** make `hardware/*.sv` check out as LF, then re-run the simulation so the saved parent run records the LF hash. A parent run saved from CRLF files keeps the CRLF hash. Two ways to do it:
   - **Repo-wide:** add `hardware/*.sv text eol=lf` to `.gitattributes` and re-checkout those files.
   - **On your laptop only:** `git config core.autocrlf false`, then `git checkout -- hardware/`.

   Then check that your ZIP's `manifest.json` → `files_sha256["hardware/matmul.sv"]` is `f81498d1…82f418c`. We refuse any mismatch rather than guess.
3. **Push your importer/validator code**, or send the exact signed-envelope field list plus one example signed with a throwaway test key. The HMAC importer is not in pushed commit `9677e03`. Your adapter needs to map our fields; we will keep our raw field names stable once you confirm them.
4. **Confirm the adapter's inputs:** `results/<run_id>/board-result.json`, `inputs.json`, `xsdb.log`, plus `build/n8_l<LANES>/implementation_manifest.json` and the `.bit`. Per your E1, the adapter should re-hash the actual bitstream and report files before signing.

## 5. Plan to the deadline (Sun 2026-11-15 12:00 PT)

| Step | Who | Needs |
|---|---|---|
| Runner `--handoff` / `--check` changes plus offline tests | Hardware | **Done** (21 offline tests pass; ZIPs generated by your own exporter load and bind once the line endings are LF) |
| Export the two ZIPs, line-ending check, push the importer | App | Section 4 |
| Run both ZIPs on the KV260 (~1 min each) and send the result folders | Hardware | Your ZIPs |
| Adapter → sign → import → render | App | Our result folders |
| Record the labelled demo runs | Both | Successful import |

Cut line if time runs short: the recorded demo uses whichever lane counts got through the full chain. If the app import isn't ready, we show the raw board result folder, labelled "board result, not yet imported".
