# SiliconOS contributor and agent guide

## Mission and scope

Build an open-source hardware architecture workbench for the November 13–15, 2026 CPVC × OCOB × CPE hackathon. Read README.md for current capability and SILICONOS_PLAN.md for strategy. The human team has two members, a KV260 available Saturday, and a partner's Windows machine with Vivado/Vitis; Vivado 2026.1.1 and a visible KV260 board preset were reported by the user. Actual Vivado synthesis and board execution remain unverified.

Current kernel contract: signed INT8 square matrix multiply, INT32 accumulation, N=8 or 16, LANES=1 or 4. Do not expand the committed workload without evidence that the existing path works. Physical deployment is the highest-risk dependency. Targets now include KV260 FPGA and custom ASIC exploration. ASIC generic Yosys synthesis is not PDK mapping, layout, timing closure or tapeout; DSP budgets apply only to FPGA.

## Evidence rules

- Never fabricate FPGA measurements, users, pilot requests, resource counts, or AI activity.
- Keep analytical, RTL-simulated, synthesized, timing-closed, and board-measured evidence distinct in data and UI.
- Target clock is an assumption until implementation and board clock configuration are verified. Simulated cycles divided by target MHz are projected microseconds, not hardware latency.
- MAC lanes do not equal mapped DSPs. Unknown DSP/LUT/BRAM values stay null. A DSP budget cannot be certified by a lane constraint.
- A wider datapath is capacity scaling, not a resource-matched architectural improvement. Disclose additional resources and excluded loading/communication costs.
- Preserve explicit unsupported requirements. A camera/complete neural model does not silently become a supported GEMM implementation.
- AI may draft specifications and explain supplied evidence. Deterministic code validates constraints, computes metrics, and ranks candidates. AI cannot create measurement fields.
- Keep API keys on the server, out of Git, logs, reports, and browser code. Missing AI configuration must be visible; no unlabeled mock fallback.

## Repository map

- `hardware/`: RTL, testbenches, synthesis preparation and Windows/board handoff.
- `siliconos/engine.py`: supported spec validation, deterministic search, simulator execution and provenance.
- `siliconos/ai.py`: optional server-side Groq chat-completions adapter.
- `server.py`: loopback development API and local SQLite persistence.
- `web/`: buildless HTML/CSS/JS workbench. The initial stack deliberately avoids Node dependency setup; Next.js is a future choice, not an implemented claim.
- `tests/`: meaningful arithmetic, lifecycle, API and constraint tests.
- `docs/`: contracts, acceptance gates and customer/pitch materials.
- `data/`: ignored runtime data; never publish raw contacts or credentials.

## Coordination

The user explicitly requested parallel agents. Assign bounded ownership and share early findings. Hardware owns `hardware/` and hardware-specific tests; product/architecture/business owns `docs/`; UI/UX owns `web/`; the coordinating agent owns backend integration and end-to-end QA. Do not overwrite another agent's active files. Agree before changing ports, schedules, API fields or evidence semantics. Keep this file current when ownership or contracts change.

## Run and verify

```sh
python3 server.py
python3 -m unittest discover -s tests -v
git diff --check
```

Python 3.10+; Icarus `iverilog` and `vvp` must be on PATH. No Python dependencies are required. Server binds to 127.0.0.1:8000; this is not a production hosting configuration. Set GROQ_API_KEY and GROQ_MODEL in the process environment to enable AI; `.env` is not auto-loaded.

Test signed extremes, zero/identity and random matrices, repeated jobs/reset behavior, unsupported spec rejection, and unverified resource budgets. Preserve raw simulator/implementation artifacts where practical. Any schedule change must update projections and cycle assertions together. Browser-check the main flow and mobile layout after substantive UI changes. Do not claim live API, Vivado, or board validation without actually running it.

## Hardware integration

`matmul.sv` custom loading ports are not AXI; `matmul_axi.sv` is a separately tested generic AXI-Lite register wrapper. It is not yet integrated into a board block design. Do not invent physical MMIO base addresses or call the wrapper a deployable bitstream. Preserve independent address/data handshakes, byte strobes and backpressure. Confirm board part, tool version, clock/reset, OS/firmware and loader compatibility. Out-of-context synthesis is not a board bitstream or timing closure. Record actual reports and hashes before enabling hardware recommendations.

## Event and customer integrity

Preserve project history in this repository. Event build window is Friday 17:00 through Sunday 12:00 Pacific; Discord updates override the published guide. No product fixes after submission cutoff. Credit libraries/public templates; do not reuse pre-event project-specific implementations.

Local pilot forms collect real opted-in interest only; distinguish interest from usage and paid commitments. State this is a student prototype. Do not send outreach without user authorization, use mass campus lists, or expose contact records. Keep customer-specific private hardware data local unless explicitly authorized.
