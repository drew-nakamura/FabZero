# Hardware ↔ app integration: open questions for the app owner

**From:** hardware side (Drew + Claude Code). **To:** app owner + your coding agent. **Date:** 2026-11-14.
**Purpose:** the matmul now runs on the KV260. Before either side automates "app → build → board → app", we need your decisions on the questions below. Each one gives our recommendation; **you make the final call** and send it back using the reply template at the end. Nothing here is decided until you answer. Where your answer conflicts with `docs/spec/`, say so and we will update the spec together.

## 1. What already exists (hardware side, verified)

All of this is on GitHub, branch `drew-branch`, commit `424c681`, folder `hw/matmul_board/`. The repo has moved to `github.com/drew-nakamura/SiliconOS`; the old URL redirects.

- **RTL used:** your unchanged `hardware/matmul.sv` + `hardware/matmul_axi.sv` from `84fcae1` (identical in `b8d9fca`), SHA256-checked.
- **Board design:** Zynq PS + AXI SmartConnect + reset, with `matmul_axi` at base address **`0xA0000000`** (4 KB). The clock `pl_clk0` is configured at 99,999,001 Hz. JTAG + xsdb from the laptop, no Linux (decision D-025).
- **Builds:** N=8 LANES=1 and N=8 LANES=4. Both meet timing at 100 MHz with DRC clean.
  - The bitstreams, XSAs, reports and hashed `implementation_manifest.json` are in `build/n8_l1/` and `build/n8_l4/`.
  - The side-by-side summary is `build/compare_n8/summary.md`.
- **Board runs (real KV260, 2026-11-14):** both PASS, with the inputs A = identity and B[i] = i − 32.
  - All 64 outputs were correct on the first run, on a repeat, and after reset + reload.
  - Measured cycles: **512** for 1 lane and **128** for 4 lanes.
  - Results are in `results/20261115T001327Z_n8_l1/` and `results/20261115T001604Z_n8_l4/`, in the format of `docs/spec/BOARD_RESULT_FILE.md`.
- **Your testbenches:** `tb_lifecycle` and `tb_axi` passed in XSIM for N = 8/16 × LANES = 1/4 (HW-REVIEW-001). They ran with `-timescale "1ns/1ps"`.

| N=8 | LANES=1 | LANES=4 |
|---|---|---|
| Cycles (board-measured) | 512 | 128 |
| Kernel time at 100 MHz (calculated) | 5.12 µs | 1.28 µs |
| matmul_axi LUT / FF / DSP | 354 / 318 / 0 | 3612 / 2470 / 0 |
| Setup slack at 100 MHz | +4.757 ns | +3.885 ns |
| Matmul power (Vivado estimate, low precision) | ~0.002 W | ~0.016 W |

**How the hardware scripts work today:**

```
python hw/matmul_board/build.py --lanes 1|4        # ~15-20 min Vivado build, prints BUILD_RESULT PASS/FAIL
python hw/matmul_board/run_board.py --lanes 1|4    # ~1 min on the board, prints MATMUL_BOARD_RESULT PASS/FAIL
       [--inputs file.json]                        #   optional {"A":[64 ints],"B":[64 ints]} signed INT8
```

**Not yet possible:**
- The build only accepts the pinned RTL above, not a SiliconeOS export.
- The runner does not take a parent run ID.
- There is no "is the board connected?" check.
- No archived SiliconeOS vectors have been run on the board.
- The app has never triggered any of this.

## 2. Please tell us your current state first

1. Which branch and commit is your current app? Is `codex/siliconos-demo` or `codex/ai-rtl-generation` the official hardware source?
2. Does the **handoff export / parent run ZIP** exist yet?
   - If so, please send one real example, plus its exact file list and JSON fields.
3. Does the app already read `board-result.json` files, or is that still to build?
4. What is tested on your side today, and how?
5. What is your demo deadline and your remaining work list?

## 3. Questions (our recommendation, then your decision)

### A. How the app calls the hardware

| # | Question | Our recommendation |
|---|---|---|
| A1 | How does the app start builds and board runs? | The app runs our Python scripts as **local subprocesses** on the build laptop (D-025: local app). No server or API. Communication goes through command-line args, exit codes and JSON files. |
| A2 | Exact commands? | `build.py --handoff <zip> --artifact-id <id>`, then `run_board.py --artifact <id> --parent-run-id <id> --inputs <file>`, and `run_board.py --check` for board health. We implement the new options. |
| A3 | What does the app read back? | Exit code 0 = pass. The app then reads `build/<artifact>/implementation_manifest.json` and `results/<run_id>/board-result.json`. It never parses console text. |
| A4 | A build takes 15–20 min. How does the app handle that? | The app starts it in the background and shows "building (~20 min)". It treats the build as finished only when the manifest file appears and the process exits 0. Runs are one at a time; the runner already locks the board. |
| A5 | Where do result folders live? | They stay in `hw/matmul_board/results/<run_id>/`, and the app reads them in place without editing. |

### B. What the app sends us (the handoff package)

| # | Question | Our recommendation |
|---|---|---|
| B1 | Package contents? | `matmul.sv`, `matmul_axi.sv`, N, LANES, `parent_run_id`, the SHA256 of each source file, plus `inputs.json` (A, B) and the expected outputs from your oracle. |
| B2 | Format? | A ZIP with a `manifest.json` listing the fields above. If your export already exists, we adapt to yours. |
| B3 | Can AI-generated RTL go to the board? | **Not for the demo.** Board runs use catalog/checked-in RTL only. Our board wrapper only works if a design keeps `matmul_axi`'s exact ports and register map (ID `0x53494c01`, offsets `0x00`–`0x24`). Generated RTL would first need that interface check plus your simulation gates. |
| B4 | N=16 on the board? | **No for the demo.** N=8 only, which is what was verified. N=16 can be built later if needed. |

### C. Avoiding re-synthesis (the 20-minute problem)

| # | Question | Our recommendation |
|---|---|---|
| C1 | Should built bitstreams be reused? | **Yes.** Cache key = SHA256(matmul.sv) + SHA256(matmul_axi.sv) + N + LANES + the build-script version. On a match, reuse the existing bitstream instantly and only build new or changed RTL. |
| C2 | Can the two existing N=8 builds count as catalog artifacts? | **Yes.** The demo path then needs zero new synthesis. Their hashes are in the manifests. |

### D. Result file details (the "TO AGREE" items in BOARD_RESULT_FILE.md)

| # | Question | Our recommendation |
|---|---|---|
| D1 | Hash format | `input_sha256` = SHA256 of the compact JSON `{"A":[...],"B":[...]}` (no spaces, keys in that order). `output_sha256` = SHA256 of the compact `[...]`. If your engine already has a canonical form, we switch to yours. |
| D2 | Linking a board run to its parent | The app passes `--parent-run-id`; we write it into `board-result.json`. The app must check that the parent exists, the source hashes match, and the input hash matches the parent's. |
| D3 | `evidence` on a failed run | `null`. The spec forbids `board_measured` on a failure. Offline tests use `"replay_test_not_board"` and can't write into `results/`. |
| D4 | Two runs in the same second | The second folder gets a `-2` suffix. Nothing is ever overwritten. |
| D5 | Fields we can't read over JTAG | `board_revision: null`, `kernel_version: null`, `image_identity: "none: JTAG boot, no operating system"`. Nothing is invented. |
| D6 | Commit result folders to Git? | Commit only the runs used in the demo. The two passing runs are already committed. |

### E. What the app shows

| # | Question | Our recommendation |
|---|---|---|
| E1 | Does the app re-check results itself? | **Yes, required:** the 7 checks in BOARD_RESULT_FILE.md "Acceptance". These are: recompute outputs with your own oracle, recompute hashes, check identity/N/LANES, cycles = N³/LANES, `timing_met`, and that the bitstream hash matches the manifest. Never trust `status` alone. |
| E2 | Board "available" indicator | Show available only if `run_board.py --check` passed within the last **5 minutes**; otherwise show "unknown". |
| E3 | Timing labels | Show **kernel cycles** (512 or 128) as the accelerator's performance. Label JTAG time (seconds) as "host transfer" and never present it as kernel speed. Kernel time = cycles ÷ configured clock, labelled "calculated". |
| E4 | Resources / power in the app | Only show them taken from our manifest and reports for the same bitstream hash. Label power as "Vivado estimate". |

### F. Ownership and demo

| # | Question | Our recommendation |
|---|---|---|
| F1 | Who owns which files? | Hardware side owns `hw/matmul_board/` (build, runner, results format). App side owns the app, handoff export, oracle and display. `docs/spec/BOARD_RESULT_FILE.md` changes need both sides' OK. |
| F2 | Integration owner / which branch is "main"? | Name one person to merge. Suggest merging `drew-branch` hardware work into your app branch once A–D are agreed. |
| F3 | Live or recorded board demo? | Recorded (D-025), labelled "Recorded real run" with the run ID visible. Hardware side records the board runs. |

## 4. Reply template

Copy this, fill it in and send it back. "Agree" is fine for any row.

```
STATE:  app branch/commit = ...   official RTL branch = ...   handoff export exists? = ...
        reads board-result.json? = ...   deadline = ...
A1: agree / change: ...      A2: ...      A3: ...      A4: ...      A5: ...
B1: ...  B2: ... (attach example export)  B3: ...      B4: ...
C1: ...  C2: ...
D1: ...  D2: ...  D3: ...  D4: ...  D5: ...  D6: ...
E1: ...  E2: ...  E3: ...  E4: ...
F1: ...  F2: ...  F3: ...
OTHER assumptions we missed: ...
```

Once we have your answers, we will update `docs/spec/BOARD_RESULT_FILE.md` with you and implement the hardware-side changes (handoff input, cache, `--parent-run-id`, `--check`).
