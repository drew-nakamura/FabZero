# Demo runbook: SiliconOS app → KV260 → app

Rehearsed end to end on Drew's laptop on 2026-11-14 at ~21:45 PT, branch `drew/demo-integration`:
- Fresh app runs `8a76e61a…` (1 lane) and `0c8276d5…` (4 lanes) were exported, run on the KV260 (`results/20261115T054545Z_n8_l1`, `results/20261115T054702Z_n8_l4`), signed and imported.
- The app shows board-measured children with 512 and 128 cycles.

## One-time setup (already done on Drew's laptop)
- Vivado 2025.2 (for rebuilds only) and Icarus Verilog 12 on PATH (`C:\iverilog\bin`, installed with `winget install Icarus.Verilog`).
- Windows **user** environment variables. They are never in Git or chat. Open a **new** terminal after setting them.
  - `SILICONOS_RUNNER_KEY` (64 hex characters) and `SILICONOS_RUNNER_KEY_ID`: the HMAC key shared by the signer and the app server. Generate it with PowerShell's `RandomNumberGenerator`; never print it.
  - `GROQ_API_KEY` and `GROQ_MODEL` (for example `openai/gpt-oss-20b`): only for the AI prompt drafting.
- Board: micro-USB **J4**, 12 V **J12**, **no SD card**. Close Vivado Hardware Manager.

## Demo steps (from the repo root, a new terminal)
1. **Start the app:** `python server.py`, then open http://127.0.0.1:8000.
2. **Board check:** `python hw/matmul_board/run_board.py --check`. It prints `BOARD_CHECK: OK`, and the sidebar shows "KV260 connected" for 5 minutes. Re-run it if the label goes stale.
3. **In the app:**
   - Describe the workload. Use **Draft spec** (AI) or **Load example · no AI needed**.
   - Keep **8×8, KV260**, and click **Run both & compare**.
   - On each result card, click **↓ FPGA handoff ZIP**.
   - Use the checked-in RTL path. **Do not use "Generate & verify RTL" for the board demo.** AI-generated RTL has no bitstream, and the runner refuses it (agreed scope B3).
4. **Run each ZIP on the board** (about 1 minute each, uses the existing bitstream because the RTL hash matches):
   `python hw/matmul_board/run_board.py --handoff "%USERPROFILE%\Downloads\siliconos-<run>-handoff.zip"`
   It prints `MATMUL_BOARD_RESULT: PASS hw\matmul_board\results\<run_id>`.
5. **Sign and import into the app:** `python hw/matmul_board/sign_result.py hw/matmul_board/results/<run_id>`
   It prints `IMPORT: OK board run … 512 cycles, 64 outputs verified`.
6. **In the app,** refresh. Under history, **KV260 board measured** → **Inspect ↗**. The card shows:
   - measured kernel cycles;
   - calculated kernel time at 99.999 MHz;
   - 64/64 outputs;
   - repeat and reset ✓;
   - Vivado timing and LUTs;
   - the measured **4.00× fewer kernel cycles** comparison once both lane counts are imported.

   The simulation card links to its board run.

## What to say (honest labels)
- "Measured on the KV260": the cycles come from the accelerator's counter on the chip, and every output was checked against the app's own reference.
- Kernel time is **calculated** (cycles ÷ configured clock). The JTAG transfer (seconds) is not accelerator speed.
- One lane versus four lanes trades about 10× the LUTs for 4× fewer cycles (arithmetic capacity, not free speed).
- Recorded runs must show the run ID ("Recorded real run", D-025).

## If something goes wrong
| Symptom | Fix |
|---|---|
| `refusing handoff ZIP … line endings` | The app checkout must have LF `hardware/*.sv`. This branch has `.gitattributes` for that; re-checkout `hardware/`. |
| `another board run holds … .runner.lock` | No run is active: delete `hw/matmul_board/results/.runner.lock`. |
| `BOARD_CHECK: FAIL` | Replug J4, power-cycle the board, close Hardware Manager, re-run `--check`. |
| `IMPORT: FAIL … not configured` | The server or signer terminal lacks `SILICONOS_RUNNER_KEY`/`_KEY_ID`: open a new terminal after setting them. |
| `IMPORT: FAIL … signature is invalid` | The signer and server use different keys: start both from new terminals. |
| `IMPORT: FAIL HTTP 404 Parent run not found` | The ZIP came from another computer's app database. Export it from this app. |
| App shows "Icarus Verilog is unavailable" | Open a new terminal (PATH), or add `C:\iverilog\bin` to PATH. |
| Live board fails during the pitch | Use the recorded run, labelled with its run ID. |
