# Focused iteration 003: Execution + Path only (/45)

## Authority and scoring surface

Drew (2026-11-14 evening) authorized continued hard research/scoring after the teammate handoff. Explicit exclusions for this loop:

- **Out of score:** Pitch & demo (/15), Real problem/real user (/25), Creative use of AI (/15). Desk research cannot honestly move those without presentation production, user observation, or a captured AI interaction.
- **Out of work:** outreach/messages, demo recording production, clean-room ownership, app signing ownership.
- **In score only:** Execution & design **/25** + Path to customers **/20** = **/45**.
- **Baseline to beat:** Execution 15 (round 002) + Path 12 (customer-path-001) = **27/45**.
- **Target:** **34/45** (same proportional bar as prior 75/100 after removing stuck rows). Report every **+3** on the /45 mean. Stop on plateau or usage-limit pressure.
- **Standard:** published guide anchors only. Score current demonstrated readiness. Do not award validation that does not exist. Do not soft-score to hit 34.

Identical packet for all judges. Root alone writes after submissions. Prior full rounds and customer-path-001 remain frozen/unedited.

## Product scope (unchanged)

SPEC 8.2 / D-025. SiliconeOS: traceable supported accelerator configuration for an engineer who reads hardware reports. Signed INT8→INT32 matmul; N=8/16; LANES=1/4; KV260 physical comparison N=8 L1 vs L4. Catalog RTL primary. Recorded evidence route accepted by founder because full synthesis is ~40 minutes; live programming is not required for this research score, but do not invent organizer exceptions. Excluded: cameras, fleet/OTA, full inference, FP16, arbitrary RTL, measured power savings, ASIC signoff, CPU/GPU superiority.

## A. Execution evidence (what changed since round 002)

### A1. Prior physical baseline (still holds)

Two routed N=8 builds (LANES=1 and 4) on `xck26-sfvc784-2LV-c`, KV260 board part 1.4, Vivado 2025.2, timing met at 10 ns constraint. Initial identity/ramp physical folders passed first/repeat/reset with counters 512/128. Accelerator+AXI LUTs 354 vs 3612 (~10.2×) for 512→128 compute counts. Power remains **vectorless estimate**, not meter-measured.

### A2. Newer app-linked board results (verified this iteration)

Root re-read both result JSONs under main checkout `hw/matmul_board/results/`:

| Folder | Parent run ID | Status | Evidence | N/L | Cycles | Outputs match | Repeat | Reset/reload |
|---|---|---|---|---|---:|---|---|---|
| `20261115T011930Z_n8_l1` | `6bccf63e-f83a-4e12-88e6-78b20d120b65` | pass | board_measured | 8/1 | 512 | true | true | true |
| `20261115T012007Z_n8_l4` | `3abe54e6-25d2-4eb7-90bf-dd3b39f3a4e9` | pass | board_measured | 8/4 | 128 | true | true | true |

Both record non-null `parent_run_id`, handoff `zip_sha256`, matching `matmul.sv` / wrapper hashes, bitstream hashes, Vivado 2025.2, JTAG/xsdb loader, `expected_outputs_match: true`, and host/programming elapsed times in nanoseconds. File SHA-256: L1 `bb3bb86c6550ec5206248cc7c9df55a9f5e03eaecfe1710d2bc35b19b75e9f44`; L4 `1a4ff036bff7f3d8c92c17377fe6caacc33cc64ab35c45eaa2e37de82ba5a26a`. Recorded 2026-11-14 ~17:20 Pacific.

### A3. Hard limits (do not upgrade)

- These runs **reuse matching pinned bitstreams**. They show ZIP/source-byte compatibility and parent linkage, **not** a fresh Vivado build from each ZIP. A product-fit checker that requires “manifest records this ZIP” / “Vivado used ZIP bytes” still rejects that stronger claim.
- App-side HMAC signing, import into history, and final **receipt export** remain unverified in this packet.
- No cold-user usability study. UI remains a plain local app; “looks like a real product” is not established.
- Host elapsed (~6.3 s L1) includes programming (~5.2 s); do not pitch fourfold end-to-end wall speedup from cycle counts alone.
- Root did not re-program the board this iteration; it verified saved JSON contents and hashes only.

## B. Path-to-customers evidence (desk research only; outreach = 0)

### B1. Carry forward (still the commercial hypothesis)

- **User:** FPGA/validation engineer comparing supported KV260 integer variants and handing evidence to another engineer.
- **Buyer to test:** engineering/hardware lead, consultancy owner, or funded lab lead who controls evaluation spend (hypothesis; not identified).
- **Entry:** free 20-minute evidence review → after readiness + founder approval, proposed **US$250 one-time** assisted N8 L1/L4 evaluation (test price, not market-validated).
- **Later mature hypothesis (separate billing unit):** **US$149/engineer/month** with ~US$30 AI allowance; research band US$99–199. Not today’s product state.
- **Switching hypothesis:** less manual reconstruction than Git/Tcl/CI/report workflows for a bounded, inspectable receipt. Free tools may already suffice — falsify if so.

### B2. New specificity this iteration (public names/places; nobody contacted)

1. **Matteo Vit / Starware Design (Cambridge, UK)** — first-person FPGA DevOps pain (source/tag/bitstream mismatch, unreproducible release PC, bus-factor releases). Public talk: CERN FPGA Developers’ Forum, 28 May 2026, “DevOps for FPGA 101”; materials on Indico. Contact page: info@starwaredesign.com. **Role in plan:** expert critique / referral candidate who already teaches the pain — **not** a lead, reply, or buyer. Sources: [intro post](https://www.starwaredesign.com/fpga-meets-devops-introduction/), [Indico talk](https://indico.cern.ch/event/1549296/contributions/7012248/), [contact](https://www.starwaredesign.com/contact/).
2. **CERN FPGA Developers’ Forum (FDF)** — recurring specialist venue where provenance/CI/HIL is on the agenda. **Place** for finding engineers who care about release identity. Not a customer list; no attendance or outreach performed.
3. **solomontesema/qcrate** — public KV260 reproducible build platform (tracked RTL/Tcl, rebuild-from-source, checksummed releases, ignore generated trees). Shows the **adjacent buyer already builds provenance discipline** on the same board family; also shows a **strong free DIY alternative**. [repo](https://github.com/solomontesema/qcrate)
4. **pccx-FPGA-NPU-LLM-kv260 runbook** — public KV260 bitstream runbook with explicit pre-deploy gates (timing/DRC/route/bitstream SHA) and evidence directory conventions. Supports that KV260 teams already document gates; SiliconeOS must beat “a careful runbook + Git.” [runbook](https://github.com/pccxai/pccx-FPGA-NPU-LLM-kv260/blob/build/v002-kv260-bitstream-runbook/docs/runbooks/v002.1-bitstream-build.md)
5. Prior routes retained: element14 FPGA Group; LogicTronix; hema; AISeQ Lab. First-ten queue still has unfilled community slots; **observed outreach/replies/payments remain zero**.

### B3. Offer ladder clarification (hypothesis)

| Stage | Price | What is sold | When it applies |
|---|---|---|---|
| Discovery | $0 / 20 min | Inspect existing authentic L1/L4 evidence | Now, research only |
| Assisted evaluation | $250 one-time | Manual-assisted packet for one supported comparison | After readiness + founder approval |
| Mature software | $149/mo | Repeatable local catalog workflow + bounded AI allowance | Only if automation/support economics proven later |

Do not pitch $149 as if the assisted $250 already sold. Do not claim either price was accepted.

### B4. Switching vs free stack (qualified, with counterevidence)

**Possible remaining gap for SiliconeOS:** one inspectable chain that binds **requirement → supported config choice → independent expected outputs → implementation metrics → physical pass/fail → parent identity** for a **human handoff**, including honest limits (estimated power, reused bitstream vs clean-room). Starware/qcrate/pccx show teams want that discipline; they also show teams can assemble it themselves.

**Counterevidence (must keep):** FuseSoC + paid support; fpga-vbs variants/reports/Git; Vivado `archive_project`; Hog/Tcl CI; qcrate’s own rebuild-from-source model; careful runbooks. “Nobody preserves FPGA provenance” is **unsupported**. Catalog 8×8 matmul may be irrelevant to a buyer’s real kernel — main commercial risk unchanged.

## C. Numbered claims for attack

**E1.** Two app-exported parent runs were executed on KV260 with `status=pass`, `evidence=board_measured`, non-null parent IDs, matching expected outputs, and passing repeat + reset/reload.  
Status: **supported** (saved JSON). Does not establish: fresh ZIP→Vivado rebuild, app import/receipt export, cold usability, or live Sunday demo polish.

**E2.** L1 vs L4 shows a real compute/resource tradeoff (512 vs 128 cycles; ~10× accelerator+AXI LUTs) with timing met.  
Status: **supported** with prior build reports. Does not establish: end-to-end wall-time speedup, DSP mapping, or measured joules.

**E3.** SiliconeOS already delivers a complete automated customer receipt from app → board → signed import.  
Status: **unsupported**. Parent-linked board JSON exists; signing/import/receipt gates remain open.

**P1.** First commercial test should be a US$250 one-time assisted N8 L1/L4 evidence evaluation after a free review.  
Status: **hypothesis**. No quotes, payments, or founder acceptance recorded.

**P2.** Mature product should charge about US$149/engineer/month with a ~US$30 AI allowance.  
Status: **hypothesis** from pricing research; not validated willingness-to-pay; not current product completeness.

**P3.** We know exactly where first users come from: element14 FPGA Group, named Kria firms, AISeQ Lab, Matteo Vit/Starware, and CERN FDF attendees.  
Status: **qualified**. Places/people are publicly specific; **none contacted**; queue ≠ acquired pipeline.

**P4.** Buyers will switch because our receipt beats their Git/Tcl/runbook stack for supported comparisons.  
Status: **hypothesis**. Adjacent pain is documented; preference for SiliconeOS is not.

**P5.** Nobody else preserves FPGA build/result provenance.  
Status: **contradicted** by FuseSoC, fpga-vbs, Vivado archives, qcrate, Starware methods, pccx runbooks.

## D. Short focused outline (not a pitch score)

Reconfigure a supported lane count → independently check outputs → deploy on KV260 → keep the parent-linked board receipt (with honest reused-bitstream limit) → offer a bounded paid evaluation of that workflow. Customer path remains untested.

## Independent review request

Score **only** Execution & design (/25) and Path to customers (/20). Return both scores, total /45, claim-by-claim status, strongest objections, and the three hardest gaps. Apply middle/top anchors strictly. If evidence is still “plausible untested model,” Path stays near 12 unless specificity clearly earns more without inventing validation. If Execution still has major product-flow gaps, stay near 15 unless app-linked parents honestly justify a step up. Do not see other judges’ scores before submitting.
