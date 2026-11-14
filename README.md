# SiliconOS

An architecture workbench for the CPVC × OCOB × CPE AI Hackathon, November 13–15, 2026.

Describe a workload, review its specification, compare supported architectures, and inspect reproducible evidence. Current scope: signed INT8 square matrix multiplication, INT32 accumulation, sizes 8/16, one/four arithmetic lanes, KV260 target.

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

Set `OPENAI_API_KEY` and `OPENAI_MODEL` in the server environment, then restart. `.env.example` lists the settings; `.env` is not automatically loaded. Never commit the key or put it in frontend code. The app uses OpenAI Responses with a strict JSON schema, then validates supported parameters server-side. Without credentials it explicitly disables AI functionality; manual editing and JSON import remain usable. API integration has not been validated against a live account yet.

## Evidence and limitations

- Analytical candidate cycle counts are projections for the checked-in RTL schedule.
- Run RTL simulation compiles real SystemVerilog, executes seeded signed inputs, and checks every output against an independent Python integer oracle. Downloaded results contain inputs, outputs, source hashes, simulator version and simulated cycles.
- Projected microseconds use a requested clock; they are not measured hardware latency. Kernel cycles exclude host loading, transfer and programming.
- DSP/LUT/BRAM usage and timing closure are unknown. DSP budgets are retained but cannot be certified. A lane is not a DSP count.
- Four lanes demonstrate additional arithmetic capacity, not a fixed-resource optimization advantage.
- An opt-in pilot-interest form stores contacts only on the local demo server. It is not a public signup funnel or evidence of commercial demand. Test fixtures use a separate temporary database.
- A generic AXI-Lite wrapper and protocol regression are included. FPGA block-design integration, actual synthesis/build/deployment, physical measurements and public hosting are still pending. See `hardware/BRINGUP.md` for the Windows/Vivado handoff and `SILICONOS_PLAN.md` for the wider plan.
- The compact initial UI uses plain HTML/CSS/JS with a Python standard-library backend to avoid dependency setup on the hardware critical path; it is not yet the proposed Next.js production stack.

## Layout

`hardware/` RTL and testbench; `siliconos/` validation, search, simulation and optional AI; `web/` workbench; `tests/` arithmetic and constraint checks.

## Credits

Icarus Verilog is an external simulator; AMD Vivado/Vitis are external proprietary build tools. OpenAI API provides optional specification generation. DM Sans and Space Grotesk are loaded from Google Fonts with system fallbacks. No third-party accelerator RTL is included. See LICENSE for the original project source.

### Judging rehearsal

Use **Load example · no AI needed**, then **Run both & compare** to execute both RTL designs on identical inputs. Editing the specification marks the displayed report as belonging to an earlier configuration. Exported new runs include the exact compiled source snapshots, their SHA-256 hashes, testbench parameters, inputs, outputs and raw simulator stdout; the replay test rebuilds them independently of the repository source files.

See [judging readiness](docs/JUDGING_READINESS.md) for the weighted rubric, four-minute demo script and outstanding customer, live-AI and board evidence gates.

For the Windows build owner, start with the [partner FPGA gameplan](docs/PARTNER_FPGA_GAMEPLAN.md): tool discovery, tonight's synthesis checkpoint, tomorrow's board integration, register smoke test and live-demo fallback.
