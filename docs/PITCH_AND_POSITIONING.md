# SiliconOS: the evidence layer for hardware experiments

## The thirty-second pitch

Hardware teams can generate another accelerator variant in minutes. The hard part is deciding whether to trust it: Which requirement produced this RTL? Did its arithmetic pass? Which configuration did the tool build? What actually ran on the board? SiliconOS connects those answers in one inspectable experiment.

In the current prototype, an engineer describes or directly configures a signed INT2, INT4, or INT8 matrix-multiply kernel, compares supported architectures, verifies outputs against an independent integer oracle, and exports the exact source, vectors, hashes, cycles, and limits of the result. The ASIC path adds generic synthesis and a separate SKY130 physical-design research record. Saved partner KV260 build and board-result artifacts for N=8 INT8 one- and four-lane configurations can be checked and imported against matching parent runs; a direct live runner connection remains pending.

**Tagline:** From hardware idea to evidence you can inspect.

## The pitch slide sequence

1. **The costly decision:** A faster-looking RTL variant is useless if the team cannot reproduce its configuration, prove its outputs, or connect it to a real build. This is the problem hypothesis; customer interviews must validate its cost and frequency.
2. **The product:** An evidence trail from reviewed requirement to candidate, verified RTL, tool artifact, and physical result. Each stage says what ran and what remains unknown.
3. **The live proof:** Enter N=8 signed INT8 matrix multiplication; compare one and four lanes under the same inputs; change the lane limit and see the available choice change; run Icarus and inspect the oracle match and observed cycles. Four lanes provide more arithmetic capacity, not a resource-matched speedup.
4. **The two implementation paths:** Show the hash-gated comparison of saved routed KV260 builds and the partner board-result import path. Show the app's Yosys generic ASIC report and, separately, the N=8/LANES=1 SKY130 mapping and physical experiments. The latest recorded SKY130 run has positive setup and hold slack and zero reported detailed-route DRC, Magic DRC, KLayout DRC and LVS errors, while slew, capacitance, fanout and antenna violations remain. It is not signoff clean.
5. **The next proof:** Link the saved KV260 results to matching parent runs, demonstrate the full loop on the board through a direct runner, and observe a qualified engineer using the workflow on a non-confidential problem. Customer demand remains an open question.

## Copy for a landing page or application

### Hero

**Build the variant. Prove the result. Keep the receipt.**

SiliconOS turns a supported hardware requirement into a reproducible accelerator experiment. Compare configurations, verify the RTL against an independent oracle, and see exactly which evidence supports each claim.

**Primary action:** Try the INT8 matrix demo  
**Secondary action:** Inspect an example evidence receipt

### Three value blocks

**Choose with context.** Compare supported architectures under explicit workload and lane constraints. The workbench shows the capacity trade and labels projected timing as projected.

**Verify what ran.** Simulation checks every output in the recorded vector set against a Python integer oracle. Source, testbench, inputs, outputs, logs and cycle observations travel with the result.

**Carry evidence forward.** Export a hash-linked handoff for FPGA integration or inspect generic ASIC synthesis. Separate tool and physical reports can extend the record without turning simulated estimates into measured claims.

### Trust strip

Open source · Exact artifact hashes · Independent arithmetic oracle · Explicit evidence levels · Unsupported requests stay unsupported

## Why this can become a business

The open core can make a team's experiments inspectable and easy to reproduce. A potential paid product would maintain private runners, team experiment history, supported board/tool combinations, and reviewable implementation evidence. The first commercial test is a narrow pilot with an engineer who already makes accelerator configuration decisions. No buyer, price, time saving, or paid demand has been validated yet.

## Phrases to use precisely

| Say | Because |
|---|---|
| “Verified on recorded test vectors” | The oracle test is real, but not universal proof. |
| “Observed simulation cycles” | They are not board latency. |
| “Projected time at a requested clock” | Clock closure and configuration are unverified. |
| “Generic ASIC synthesis in the app” | The app report is not technology mapped. |
| “Separate SKY130 mapping and physical experiment” | The recorded physical runs have unresolved violations. |
| “Saved KV260 build and board artifacts, subject to hash-gated import” | The local API does not have a direct live board runner. |

Keep the public claim as strong as the underlying artifact. The product's strongest advantage is that a user can see the boundary of every result.
