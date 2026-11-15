# SiliconOS

**From hardware idea to evidence you can inspect.** An open-source architecture workbench for the CPVC × OCOB × CPE AI Hackathon, November 13–15, 2026.

Describe a workload, review its specification, compare supported architectures, and inspect reproducible evidence. The current kernel is signed INT2, INT4, or INT8 square matrix multiplication with INT32 outputs, sizes 8/16, and one, two, or four arithmetic lanes. The default is INT8. SiliconOS connects simulation, synthesis, implementation artifacts, and physical results without treating them as interchangeable.

The core pitch is simple: an accelerator variant only matters if another engineer can identify its requirement, reproduce its build, check its arithmetic, and see what actually ran. [Pitch and positioning](docs/PITCH_AND_POSITIONING.md) gives a judge-ready narrative; [judging readiness](docs/JUDGING_READINESS.md) lists the remaining proof gates.

## Run locally

Requires Python 3.10+; no Python packages needed. RTL simulation requires `iverilog` and `vvp` on PATH.

```sh
python3 server.py
```

Open http://127.0.0.1:8000. The server binds to loopback; it is a development server, not a public deployment. Runs and local activity events persist in ignored `data/siliconos.db`.

```sh
python3 -m unittest discover -s tests -v
```

## AI configuration

Set `GROQ_API_KEY` and `GROQ_MODEL` in the server environment, then restart. `.env.example` lists the settings; `.env` is not automatically loaded. Never commit the key or put it in frontend code. Specification drafting uses Groq chat completions with a strict JSON schema and server-side parameter validation; RTL generation requests raw SystemVerilog and verifies it separately. Choose a model that supports strict structured outputs for specification drafting (for example `openai/gpt-oss-120b` or `openai/gpt-oss-20b`). Without credentials it explicitly disables AI functionality; manual editing and JSON import remain usable. Automated provider fixtures do not establish live account availability or generation quality.

## Generate and verify RTL

Describe a supported workload, review the editable specification, then click **Generate & verify RTL**. Groq generates new SystemVerilog for the exact signed INT8 → INT32 `matmul` interface. The button requires configured AI and Icarus Verilog; **Custom ASIC** also requires Yosys. The selected lane count is 1 for `minimize_lanes`, otherwise the reviewed lane limit. This selection is not a proof of optimality or physical resource use.

The server rejects incompatible or disallowed source before running tools. Accepted candidates must compile with the unchanged `hardware/tb.sv`, produce every expected Python integer-oracle output, and pass an independent execution-cycle monitor. For ASIC targets, the same source must also pass real Yosys synthesis and synthesized-netlist oracle checks. Any stage failure returns a visible error and saves no run or activity event; no candidate source is displayed before verification succeeds. Prior verified reports remain available.

Successful generated simulation has evidence `ai_generated_rtl`, labeled **AI-generated RTL, verified by simulation against an integer oracle**. It is distinct from checked-in `rtl_simulation`. ASIC results retain that simulation report and a separate nested `generic_synthesis` report with `source_origin: ai_generated_rtl`. Exports include source snapshots and SHA-256 hashes, the unchanged testbench, trusted monitor, parameters, vectors, outputs and tool logs. Editing the workload prompt or specification marks generated reports stale.

Per-run verification covers the recorded vectors and parameter choice; it is not formal equivalence or proof for every input. Generated schedules may differ from checked-in analytical projections. DSP/LUT/BRAM remain `null`; generic cells are not area, and neither route establishes physical or board performance. The static gate is a restricted-language check, not an OS sandbox for a public hostile-code service. See [AI RTL generation](docs/AI_RTL_GENERATION.md) for the API, replay commands and evidence boundaries.

## Evidence and limitations

- Analytical candidate cycle counts are projections for the checked-in RTL schedule.
- Run RTL simulation compiles real SystemVerilog, executes seeded signed inputs, and checks every output against an independent Python integer oracle. Downloaded results contain inputs, outputs, source hashes, simulator version and simulated cycles.
- Projected microseconds use a requested clock; they are not measured hardware latency. Kernel cycles exclude host loading, transfer and programming.
- DSP/LUT/BRAM and timing values require a matching Vivado report; they cannot be inferred from lane count. The saved routed N=8 INT8 KV260 build reports are inspectable through the build comparison when the exact original RTL hashes match. They do not certify the current edited RTL or a board measurement.
- Four lanes demonstrate additional arithmetic capacity, not a fixed-resource optimization advantage.
- An opt-in pilot-interest form stores contacts only on the local demo server. It is not a public signup funnel or evidence of commercial demand. Test fixtures use a separate temporary database.
- A generic AXI-Lite wrapper and protocol regression are included. The partner has supplied saved KV260 build and board-result artifacts for N=8 INT8 one- and four-lane configurations; the app-linked import verifies hashes, implementation reports, outputs and lifecycle evidence before accepting a `board_measured` child result. Direct live runner connection and public hosting remain pending. See [KV260 build comparison](docs/KV260_BUILD_COMPARISON.md), `hardware/BRINGUP.md`, and `SILICONOS_PLAN.md`.
- The compact initial UI uses plain HTML/CSS/JS with a Python standard-library backend to avoid dependency setup on the hardware critical path; it is not yet the proposed Next.js production stack.

## Layout

`hardware/` RTL and testbench; `siliconos/` validation, search, simulation and optional AI; `web/` workbench; `tests/` arithmetic and constraint checks.

## Credits

Icarus Verilog is an external simulator; AMD Vivado/Vitis are external proprietary build tools. The Groq API provides optional specification and candidate RTL generation. DM Sans and Space Grotesk are loaded from Google Fonts with system fallbacks. No third-party accelerator RTL is included. See LICENSE for the original project source.

### Judging rehearsal

Use **Load example · no AI needed**, then **Run both & compare** to execute both RTL designs on identical inputs. Editing the specification marks the displayed report as belonging to an earlier configuration. Exported new runs include the exact compiled source snapshots, their SHA-256 hashes, testbench parameters, inputs, outputs and raw simulator stdout; the replay test rebuilds them independently of the repository source files.

See [judging readiness](docs/JUDGING_READINESS.md) for the weighted rubric, four-minute demo script and outstanding customer, live-AI and board evidence gates.

For the Windows build owner, start with the [partner FPGA gameplan](docs/PARTNER_FPGA_GAMEPLAN.md): tool discovery, tonight's synthesis checkpoint, tomorrow's board integration, register smoke test and live-demo fallback.

### Custom ASIC exploration

Select **Custom ASIC** to retain RTL verification and enable **Synthesize generic logic**. Requires `yosys`, `iverilog`, and `vvp` on PATH. The server runs Yosys, then simulates the generated netlist against the integer reference before accepting a result. Download the Verilog netlist, synthesis script or complete JSON evidence bundle. The script expects the matching `matmul.sv` source included in that bundle.

The app's ASIC report is generic synthesis and netlist-oracle evidence. Separately, the N=8/LANES=1 INT8 research baseline was mapped to the SKY130 HD library and taken through physical implementation experiments. The latest recorded route has positive setup/hold slack and zero reported detailed-route DRC, Magic DRC, KLayout DRC and LVS errors, but unresolved slew, capacitance, fanout and antenna violations. It is not signoff clean or fabrication ready. See [ASIC workflow](docs/ASIC_WORKFLOW.md) and its linked evidence snapshots.

### Reusable RTL catalog

The **Reusable RTL** section lists the two executable compute recipes and a separately qualified upstream utility. **Build recipe** exports deterministic selection, parameter values, exact source snapshots and hashes without calling AI. `/api/catalog` exposes metadata; `/api/plan` accepts a supported spec and optional allowlisted block ID/lane choice. Unknown IDs and unqualified compositions are rejected. New curated simulation/synthesis reports include the build recipe. Groq receives only compact executable catalog metadata, not whole repositories.

`hardware/vendor/wb2axip/skidbuffer.v` is an unmodified upstream ZipCPU utility pinned in its adjacent manifest, with its Apache-2.0 license retained. Our local test qualifies only DW=8, registered outputs, initialization disabled, low-power mode disabled and passthrough disabled. It tests ordering, backpressure, drain, reset and restart. The block is **not** inserted into the matrix datapath and is not board- or ASIC-implementation-qualified. Run `python3 -m unittest tests.test_catalog -v` to check provenance and the local protocol regression. See [IP shortlist](docs/RTL_IP_SHORTLIST.md) before adding other blocks.

### One-click verified builds

Select Custom ASIC, then **Build verified design** under Reusable RTL. `/api/build` selects an allowlisted recipe, simulates RTL, runs Yosys generic synthesis and verifies the resulting netlist. The operation saves one atomic evidence bundle only after success, with matching source hashes. FPGA-target builds stop at RTL simulation. The activity bar is indeterminate; it does not estimate tool completion. Neither route establishes physical timing or produces GDSII.

Groq transient connection, rate-limit and server errors receive at most one automatic retry. Authentication, model/schema rejection and malformed responses fail visibly without weakening validation. Configure `GROQ_API_KEY` and `GROQ_MODEL` in the server process; a key saved in another terminal/app or an unloaded `.env` is not automatically inherited.

### Partner handoff API

The [shared demo product and FPGA integration specification](docs/DEMO_PRODUCT_AND_FPGA_SPEC.md) is the authoritative scope, interface, evidence, ownership and acceptance contract for the product owner and Windows/Vivado owner.

`GET /api/runs/<run-id>/handoff.zip` exports an accepted run as a portable archive. It verifies the stored source hashes, input bounds and independent reference outputs before export. The archive contains exact RTL/testbench snapshots, input vectors, expected outputs, file hashes, replay instructions, and separately labeled current integration aids. The latter do not prove that the AXI wrapper works with the archived kernel on a board. The confirmed partner tools are Vivado/Vitis 2025.2 on Windows 11; board SK-KV260-G. Exact device part, firmware/OS and address mapping remain to verify.

`POST /api/runs/<run-id>/board-result` accepts a separate physical child report only after trusted-runner HMAC authentication, implementation-manifest binding, complete output/oracle checks, repeat-without-reload evidence and reset-recovery evidence. Configure `SILICONOS_RUNNER_KEY` and `SILICONOS_RUNNER_KEY_ID` in both trusted processes, then sign the runner output with `python -m siliconos.board unsigned-board-result.json board-result.json`. Never put the secret in Git, browser code, result JSON or logs. The endpoint does not make the board live; `/api/status` keeps `board=false` until a direct runner health check exists.

For the partner's saved app-linked KV260 results, use the local adapter instead of uploading the raw `board-result.json`. Start `python3 server.py` with `SILICONOS_RUNNER_KEY` (at least 32 bytes) and `SILICONOS_RUNNER_KEY_ID` set, then run this in another shell with the **same** two variables:

```sh
python3 -m siliconos.import_drew hw/matmul_board/results/20261115T011930Z_n8_l1 hw/matmul_board/build/n8_l1 data/handoff_exports/siliconos-6bccf63e-f83a-4e12-88e6-78b20d120b65-n8-l1-handoff.zip
python3 -m siliconos.import_drew hw/matmul_board/results/20261115T012007Z_n8_l4 hw/matmul_board/build/n8_l4 data/handoff_exports/siliconos-3abe54e6-25d2-4eb7-90bf-dd3b39f3a4e9-n8-l4-handoff.zip
```

The adapter first checks the ZIP, actual bitstream, implementation reports, build artifacts, inputs, outputs, cycles and lifecycle results, then signs and posts the mapped result. The original parent simulations must exist in the server database. The raw result and artifact files remain unchanged. Run `python3 -m unittest tests.test_board -v` for an offline import-path check; it does not run the board.

For Groq connection failures, compare the same configured server on a known-working network. The user reports successful access on a mobile hotspot and intermittent failures on campus Wi-Fi; network filtering/DNS/TLS/proxy behavior is a hypothesis, not a verified diagnosis. Keep TLS verification enabled. Exported shell variables must be inherited by the actual server process. Never send keys in diagnostics or archives.
