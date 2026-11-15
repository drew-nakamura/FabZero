# SiliconeOS focused research and score 003

**27/45 mean — unchanged vs baseline 27. Plateau. No +3 report trigger.** Independent totals: technical 26, customer 27, pitch/integrity 28. Range **26–28**.

November 14, 2026 evening, America/Los_Angeles. Drew resumed after the teammate handoff and authorized a research-only loop: leave out rows that desk research cannot move, score hard, report every +3 on the reduced scale, stop on plateau or usage pressure. This report records both the **research findings** and the **judge outcome**. It does not approve product scope, claim unfinished work passed, or replace earlier full-product rounds.

## Scope of this iteration

| In | Out |
|---|---|
| Execution & design (/25) | Pitch & demo (/15) — presentation later |
| Path to customers (/20) | Real problem / real user (/25) — needs observation |
| Desk research + verifying saved board JSON | Creative use of AI (/15) — needs a shown interaction |
| Target **34/45** (same bar as prior 75/100 on remaining rows) | Outreach / sending messages |
| | Owning clean-room builds or app signing work |

**Denominator:** 25 + 20 = **/45**.  
**Baseline:** Execution 15 (round 002) + Path 12 (customer-path-001) = **27/45**.

## Research findings

### 1. App-linked board evidence (verified, with limits)

Root re-read the newer result folders under `hw/matmul_board/results/` (main checkout). Both are real saved board results, not slides.

| Folder | Parent run ID | Status | Evidence | N / LANES | Cycles | Outputs match | Repeat | Reset/reload |
|---|---|---|---|---|---:|---|---|---|
| `20261115T011930Z_n8_l1` | `6bccf63e-f83a-4e12-88e6-78b20d120b65` | pass | board_measured | 8 / 1 | 512 | true | true | true |
| `20261115T012007Z_n8_l4` | `3abe54e6-25d2-4eb7-90bf-dd3b39f3a4e9` | pass | board_measured | 8 / 4 | 128 | true | true | true |

Also present in both: handoff `zip_sha256`, matching `matmul.sv` / wrapper hashes, bitstream hashes, Vivado 2025.2, JTAG/xsdb, host and programming elapsed times. File SHA-256: L1 `bb3bb86c6550ec5206248cc7c9df55a9f5e03eaecfe1710d2bc35b19b75e9f44`; L4 `1a4ff036bff7f3d8c92c17377fe6caacc33cc64ab35c45eaa2e37de82ba5a26a`. Recorded ~17:20 Pacific on November 14.

**What this establishes:** app-exported parents can be accepted by the runner and executed on KV260 with independent expected-output checks and repeat/reset behavior, with non-null parent linkage.

**What this does not establish:**

- Fresh Vivado build from each ZIP’s bytes (pinned bitstreams were reused).
- App HMAC signing, history import, or final receipt export.
- Cold usability or a polished product UI.
- Fourfold end-to-end wall-time speedup (programming dominates host elapsed time).
- A live re-program in this research pass (JSON contents/hashes only).

### 2. Customer-path desk research (no outreach)

Prior customer-path packet already had: user/buyer hypotheses, US$250 assisted entry, element14 / LogicTronix / hema / AISeQ routes, outreach count zero, and a unanimous **12/20**.

**New public specificity added this pass:**

1. **Matteo Vit / Starware Design (Cambridge, UK)** — first-person FPGA DevOps pain (source/tag/bitstream mismatch, unreproducible release PC, bus-factor releases). CERN FPGA Developers’ Forum talk, 28 May 2026, “DevOps for FPGA 101.” Public contact: info@starwaredesign.com. Role in plan: expert critique / referral candidate — **not** a lead, reply, or buyer. Sources: [intro](https://www.starwaredesign.com/fpga-meets-devops-introduction/), [Indico](https://indico.cern.ch/event/1549296/contributions/7012248/), [contact](https://www.starwaredesign.com/contact/).
2. **CERN FPGA Developers’ Forum (FDF)** — specialist venue where provenance/CI/HIL is discussed. A place to find engineers who care about release identity; not a customer list.
3. **solomontesema/qcrate** — public KV260 reproducible platform (rebuild-from-source, checksummed releases). Shows adjacent buyers already practice provenance on the same board family, and that a strong free DIY alternative exists. [repo](https://github.com/solomontesema/qcrate)
4. **pccx KV260 bitstream runbook** — explicit pre-deploy gates (timing/DRC/route/bitstream SHA) and evidence-directory conventions. SiliconeOS must beat “careful runbook + Git,” not claim to invent gates. [runbook](https://github.com/pccxai/pccx-FPGA-NPU-LLM-kv260/blob/build/v002-kv260-bitstream-runbook/docs/runbooks/v002.1-bitstream-build.md)

**Offer ladder (still hypotheses):**

| Stage | Price | Deliverable | Status |
|---|---|---|---|
| Discovery | $0 / 20 min | Inspect existing authentic L1/L4 evidence | Research only |
| Assisted evaluation | $250 one-time | Manual-assisted packet for one supported comparison | After readiness + founder approval |
| Mature software | $149/mo (+ ~$30 AI allowance) | Repeatable local catalog workflow | Later; not today’s completeness |

**Observed commercial counts remain zero:** invitations, replies, qualified conversations, quotes, payments.

### 3. Claim ledger after this pass

| ID | Claim (short) | Status |
|---|---|---|
| E1 | App-linked L1/L4 board passes with parents, match, repeat/reset | **Supported** (saved JSON) |
| E2 | L1 vs L4 compute/resource tradeoff with timing met | **Supported** (JSON + prior builds) |
| E3 | Complete automated app→board→signed receipt | **Unsupported** |
| P1 | Test US$250 one-time assisted evaluation | **Hypothesis** |
| P2 | Mature US$149/mo | **Hypothesis** |
| P3 | Exact first-user places/people known | **Qualified** (named publicly; none contacted) |
| P4 | Buyers switch for easier receipt handoff | **Hypothesis** |
| P5 | Nobody else preserves FPGA provenance | **Contradicted** |

## Judge scores

| Judge | Execution | Path | Total /45 |
|---|---:|---:|---:|
| Technical | 15 | 11 | 26 |
| Customer / business | 16 | 11 | 27 |
| Pitch / integrity | 16 | 12 | 28 |
| **Mean** | **15.7** | **11.3** | **27.0** |

Path mean **11.3** is slightly **below** the earlier focused **12/20**, because new sources also strengthened free alternatives. Execution mean **15.7** is a thin step above round-002’s **15**, not enough to move the /45 total.

Judges agreed: parent-linked JSON is evidence hygiene inside the middle Execution band; naming public people without contact is not a pipeline; uniqueness claims are contradicted by FuseSoC, fpga-vbs, Vivado archives, qcrate, Starware methods, and pccx runbooks.

## Why the score did not rise

Desk research improved the **map** (who exists publicly, what free stacks already do, how offers ladder). It did not create **validation**. Harsh anchors require tested switch/pay intent for Path above middle, and a cold, complete product flow for Execution well above middle. Those need actions.

## What would move +3 or more (actions)

1. Verified app signing → import → receipt export (and ideally clean-room ZIP→Vivado→board binding).
2. One qualified engineer observation plus a real budget-owner response to the exact US$250 offer.
3. Later (out of this loop): recorded product journey and a shown useful AI drafting/check interaction.

## Artifacts

- Packet: `research_notes/SiliconeOS pitch claim review/focused-003-packet.md`  
  SHA-256 `81d275c6eca9bda80fa47b6b673e42ab758cd05123564b4b69ed47c4e8568841`
- Scores: `focused-003-scores.json`
- Judges: `focused-003-judge-technical.md`, `focused-003-judge-customer.md`, `focused-003-judge-pitch-ai.md`
- Prior full-product mean remains **46.3/100** (round 002); this focused pass does **not** recompute a /100 total.

**Stopped:** plateau at 27/45; other-models usage limit already encountered; further desk-only iterations not expected to clear the blockers above.
