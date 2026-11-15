# FabZero product progress

Updated: 2026-11-14 (America/Los_Angeles).

## Direction

- Help hardware startups explore a component idea through an FPGA demonstration without requiring RTL expertise.
- Target the available AMD Kria KV260 for the hackathon demonstration.
- The intended demonstration requires the generated component to execute on the physical board; simulation or synthesis alone does not establish that outcome.

## Current state

- Product scope and architecture are still being discussed. There is no approved build specification recorded by this progress update.
- Exploratory planning and decision records are maintained under `docs/spec/`; publish intentional product artifacts when ready.
- KV260 board bring-up is verified (2026-11-14), see `hw/bringup/README.md`. The factory boot console answered a hello world. A test design built with Vivado 2025.2 (timing met, no DRC errors) was loaded over JTAG, and the FPGA logic returned the expected ID, a running counter and correct `3x+1` results, again after a power cycle. This is a board/toolchain baseline, not product functionality.
- No product implementation (prompt-to-RTL, customer component) has been published yet.
- Development-agent configuration and personal workflow documents are kept local. The GitHub branch is reserved for the product and its decisions/progress.

## Next milestones

1. Agree on the smallest complete customer demonstration and its acceptance criteria.
2. ~~Establish the actual toolchain and a reproducible KV260 build/load/run baseline.~~ Done; see `hw/bringup/`.
3. Implement and test the accepted product slice, recording evidence for each completed stage.
