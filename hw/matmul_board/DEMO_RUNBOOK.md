# Demo runbook: SiliconOS app → KV260 → app

The terminal flow was rehearsed end to end on Drew's laptop on 2026-11-14 at ~21:45 PT, branch `drew/demo-integration`:
- Fresh app runs `8a76e61a…` (1 lane) and `0c8276d5…` (4 lanes) were exported, run on the KV260 (`results/20261115T054545Z_n8_l1`, `results/20261115T054702Z_n8_l4`), signed and imported.
- The app shows board-measured children with 512 and 128 cycles.

The in-app **Build it and run it on the KV260** button (added the same night) runs those same commands from the server. Through the app's API it ran both designs on the board at ~23:09 (board runs `6e89be5c…` 512 cycles and `8924f85e…` 128 cycles, 38 s in total). Rehearse it once in the browser before recording.

## One-time setup (already done on Drew's laptop)
- Vivado 2025.2 (for rebuilds only) and Icarus Verilog 12 on PATH (`C:\iverilog\bin`, installed with `winget install Icarus.Verilog`).
- Windows **user** environment variables. They are never in Git or chat. Open a **new** terminal after setting them.
  - `SILICONOS_RUNNER_KEY` (64 hex characters) and `SILICONOS_RUNNER_KEY_ID`: the HMAC key used by the signer and the app server. Generate it with PowerShell's `RandomNumberGenerator`; never print it.
  - `GROQ_API_KEY` and `GROQ_MODEL` (`openai/gpt-oss-20b`): the AI prompt drafting. Set on 2026-11-14 and checked with one live request.
- Board: micro-USB **J4**, 12 V **J12**, **no SD card**. Close Vivado Hardware Manager.

## Demo (from the repo root, a new terminal)
1. **Start the app:** `python server.py`, then open http://127.0.0.1:8000.
2. **01 Describe:** type the workload, for example "A fast 8×8 INT8 matrix multiply on my KV260, up to 4 lanes, 100 MHz", then click **Generate specification**. Without AI, click **Use the example · no AI**. Wait about a minute between AI clicks (Groq rate limit).
3. **02 Specification & architecture** appears. It shows the AI's spec with the source of each field, and the two architectures (1-lane sequential MAC vs 4-lane parallel MAC array), each with "KV260 bitstream ready". Nothing has run yet. Click **▶ Build it and run it on the KV260**.
4. **The steps appear one by one** (about 40–60 s in total; the progress bar at the top follows along):
   - **03 RTL verified and packaged:** the start of `matmul.sv`, simulated cycles, 64/64 outputs, and the handoff ZIP.
   - **04 Vivado implementation complete:** the bitstream built from this exact RTL (reused, not rebuilt). It shows timing slack, Fmax estimate, LUT/FF/DSP/BRAM, power estimate, DRC, an excerpt of `timing_summary.rpt`, and links to every report.
   - **05 The KV260 responds:** the JTAG cable, the FPGA and the ARM debug port. Per design: measured cycles, 64/64, repeat/reset, an excerpt of the JTAG transcript, and the signed import.
   - **06 Results:** 4.00× fewer cycles and 10.2× the LUTs, a 1-vs-4 chart (cycles, LUTs, flip-flops, Fmax), and the full table.
5. **Run history & tools** (collapsed at the bottom) has the run records and **Show the last recorded run**.

**Do not use "Generate & verify RTL" for the board demo.** AI-written RTL has no bitstream (a new Vivado build takes 10–12 minutes per configuration), and the runner refuses it (agreed scope B3). **16×16** runs stop after simulation for the same reason.

## Terminal fallback (same tools, by hand)
1. `python hw/matmul_board/run_board.py --check` prints `BOARD_CHECK: OK`.
2. In the app, after **Run both & compare**, click **↓ FPGA handoff ZIP** on each result card.
3. `python hw/matmul_board/run_board.py --handoff "%USERPROFILE%\Downloads\siliconos-<run>-handoff.zip"` prints `MATMUL_BOARD_RESULT: PASS hw\matmul_board\results\<run_id>`.
4. `python hw/matmul_board/sign_result.py hw/matmul_board/results/<run_id>` prints `IMPORT: OK board run … 512 cycles, 64 outputs verified`.

## What to say (honest labels)
- "Measured on the KV260": the cycles come from the accelerator's counter on the chip, and every output was checked against the app's own reference.
- Kernel time is **calculated** (cycles ÷ configured clock). The JTAG transfer (seconds) is not accelerator speed.
- Power is a **Vivado estimate**, not measured.
- The bitstream was **built earlier** (about 10 minutes in Vivado) and is **reused** because the RTL's SHA-256 matches. Vivado does not run live.
- One lane versus four lanes trades about 10× the LUTs for 4× fewer cycles (arithmetic capacity, not free speed).
- Recorded runs must show the run ID ("Recorded real run", D-025). **Show last recorded run** labels them that way.

## If something goes wrong
| Symptom | Fix |
|---|---|
| Step 5 fails "board not detected" | Replug J4, power-cycle the board, close Hardware Manager, press **Check board**. |
| Step 6 fails `another board run holds … .runner.lock` | No run is active: delete `hw/matmul_board/results/.runner.lock`. |
| Step 7 fails `not configured` | The server lacks `SILICONOS_RUNNER_KEY`/`_KEY_ID`: start `python server.py` from a new terminal. |
| Step 4 fails "not built from this RTL" | `hardware/*.sv` changed or has CRLF line endings: re-checkout `hardware/` (this branch has `.gitattributes`). |
| AI shows "not configured" | Set `GROQ_API_KEY` and `GROQ_MODEL`, then restart the server from a new terminal. |
| App shows "Icarus Verilog is unavailable" | Open a new terminal (PATH), or add `C:\iverilog\bin` to PATH. |
| Live board fails during the pitch | Under **Run history & tools**, click **Show the last recorded run** and say it is recorded, with its run ID. |
