# First working slice — November 13

## Working locally

- Browser workbench: editable specification, JSON import, deterministic candidate search, lane-limit filtering, persistent experiment history and JSON export.
- Icarus execution of actual INT8 RTL for N=8/16 and LANES=1/4, with independent integer output validation.
- Matched comparison requires identical spec, inputs, output hash, source hashes, simulator and evidence type.
- Generic AXI-Lite wrapper with protocol tests, kernel lifecycle tests, Windows Vivado out-of-context synthesis preparation.
- Local opt-in pilot-interest storage with consent. No real customer contacts have been collected in this task; test fixtures use a separate temporary database.
- Repository agent guide, MIT license, specification contract and customer/pitch handoff.

## Verified

Python suite covers 100 random matrix cases across four configurations plus zero, identity and signed-extreme inputs; lifecycle/reset/repeat checks; AXI channel order/strobes/backpressure; invalid specs; AI adapter response handling with mocked responses; consent persistence. Browser QA ran both lane configurations and observed 512 versus 128 simulated kernel cycles for 8×8 with matching outputs. Lane limit 1 excludes the four-lane candidate. Layout has no horizontal document overflow at 390 and 1440 pixel viewport widths. JavaScript syntax checked by the UI agent.

These runs are developer QA, not customer usage. The 4× cycle ratio spends four lanes and excludes input transfer; it is not a fixed-resource improvement or measured FPGA speedup.

## Not yet verified or implemented

- Live AI requests: adapter exists but API credentials/model are not configured. Provider/API eligibility question is pending. Mocked adapter tests do not establish live service availability or extraction quality.
- Vivado synthesis: script exists, but no available Vivado execution on this Mac. Need partner's Windows tool version and installed part/board definition.
- Board block design, clock/reset/address map, bitstream, OS/firmware packaging, loader and physical measurements. KV260 available tomorrow.
- Real DSP/LUT/BRAM mapping and timing closure. Budgets are preserved but not certified.
- Resource-matched optimization beyond lane scaling; full inference/camera workloads; power or energy measurement.
- Public hosting and qualified customer validation.

## Next execution gates

1. Configure an API-capable provider locally and validate one supported and one unsupported natural-language request.
2. Partner runs the explicit-part synthesis script and inspects reports; integrate the AXI top in a KV260 PS block design.
3. Tomorrow prove identity and scratch/address readback, then a correct one-lane physical job and matching four-lane job.
4. Attach actual implementation reports and board manifests before enabling physical recommendations.
5. Observe a target engineer using the end-to-end flow; publish the try link before the Saturday commitment deadline.

## Judging evidence still needed

The supplied rubric weights execution/design 25%, real problem/user 25%, path to customers 20%, pitch/demo 15%, and creative AI 15%; these are not achieved scores. See [judging readiness](JUDGING_READINESS.md) for the acceptance gates and four-minute script.

- No qualified-user observation, specific customer incident, acquisition-channel validation, or agreed customer workload is recorded here. The combined problem/customer criteria account for 45%; developer tests and pilot form availability do not establish that evidence.
- Live AI needs supported, ambiguous and unsupported prompt checks. Mocked responses do not prove extraction quality or the usefulness of assumption review.
- A timed rehearsal on the presentation machine and clearly labeled real-run backup remain to be recorded. Public try-link readiness is separate from the working loopback app.
- Physical claims require a fresh correct board job and artifact/clock provenance; a simulated AXI wrapper or out-of-context synthesis report is insufficient.

## Latest integration QA

Coordinator-reported QA: one-click paired execution produced 512/128 simulated cycles with matching outputs; the no-AI sample path works; editing the spec immediately marks the displayed result stale; lane limit 1 disables paired comparison. Browser checks at 390 and 1440 pixels found no horizontal overflow. Export now contains exact source snapshots, raw simulator stdout and parameters; its replay test passed. A hardware regression for the stale-done race passed. These remain developer/simulation checks, not live AI, physical hardware or customer evidence.
