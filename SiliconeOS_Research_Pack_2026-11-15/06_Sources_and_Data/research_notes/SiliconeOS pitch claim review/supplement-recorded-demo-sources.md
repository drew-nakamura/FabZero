# Supplemental primary-source notes for the recorded demo

Checked November 14, 2026, America/Los_Angeles. Research supplement authorized by Drew while he gathers execution data. No judge rerun or score update. These are source paraphrases and scope notes, not full downloaded page snapshots. Source publication dates are given only when displayed; rolling pages may change.

Named cases below are adjacent engineering examples hosted by a supplier. They establish described tasks, not observed SiliconeOS demand or independent comparative results. Documentation establishes existing capabilities and methods, not successful execution of this product.

## R01: Lunar Energy: variant testing and traceability

- Source: [Lunar Energy: variant testing and traceability](https://www.ni.com/en/solutions/energy/case-studies/scaling-power-conversion-test-startup-speed.html). NI-hosted customer-authored case; Ash Mistry, Lunar Energy; publication date not displayed.
- Location: The Challenge; Why Fragmented Test Approaches Fall Short; Scaling Output Without Scaling Headcount.
- Observed content: Lunar describes fragmented tools and duplicated test logic making result correlation across variants/revisions difficult. Its chosen solution uses existing NI products.
- Limit/counterevidence: Adjacent power-electronics testing, supplier-hosted account; no SiliconeOS use, FPGA-receipt demand, independent savings study or transferable benefit.
- Inspection: Root opened original and relevant full sections.

## R02: Danfoss: frequent configuration changes and repeatable tests

- Source: [Danfoss: frequent configuration changes and repeatable tests](https://www.ni.com/en/solutions/transportation/case-studies/improve-test-coverage-documentation-and-traceability-by-integrating-python-automation-with-hil-testing.html). NI-hosted customer-authored case; Dirk Runge, Danfoss; publication date not displayed.
- Location: Working with MATS; Adding a Python interface; The Outcome.
- Observed content: The author describes hardware/software test configurations changing multiple times a day and Python-based automation producing reports and repeatable tests.
- Limit/counterevidence: Adjacent ECU/HIL workflow, not our matmul workload or a customer interview; NI and custom scripts already solve parts of the task.
- Inspection: Root opened original and relevant full sections.

## R03: AMD: validation at separate design stages

- Source: [AMD: validation at separate design stages](https://docs.amd.com/r/2025.2-English/ug949-vivado-design-methodology/Validating-at-Each-Design-Stage). AMD UG949, 2025.2, release 2025-11-20.
- Location: Validating at Each Design Stage.
- Observed content: AMD recommends checking design budgets and timing constraints throughout the design flow.
- Limit/counterevidence: Methodology supports separate stage evidence; it does not certify our runs or customer value.
- Inspection: Root opened version matching recorded project tools.

## R04: AMD: routed timing evidence

- Source: [AMD: routed timing evidence](https://docs.amd.com/r/2025.2-English/ug906-vivado-design-analysis/Report-Timing-Summary). AMD UG906, 2025.2, release 2025-12-10.
- Location: Report Timing Summary, final paragraphs.
- Observed content: Post-synthesis net delay is estimated; implemented analysis uses routing information. Timing signoff uses the completely routed design and route status.
- Limit/counterevidence: A synthesis report or requested frequency does not establish routed timing; no project timing result was inspected in this supplement.
- Inspection: Root opened original and final paragraphs.

## R05: AMD: matrix multiplication already has established implementations

- Source: [AMD: matrix multiplication already has established implementations](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/vitis/vitis-libraries/vitis-blas.html). AMD live product/library page; undated, checked 2026-11-14.
- Location: Functions; Function Implementation Types.
- Observed content: The library includes general matrix multiplication and hardware/kernel/software interfaces.
- Limit/counterevidence: Supports matmul as a recognized building block and an existing alternative; no drop-in compatibility, datatype/board equivalence, performance comparison or novelty for our kernel.
- Inspection: Root opened original.

## R06: AMD: parallelism can be limited by interface bandwidth

- Source: [AMD: parallelism can be limited by interface bandwidth](https://docs.amd.com/r/2025.2-English/Vitis-Tutorials-Vitis-HLS/Compare-results). AMD XD261, 2025.2, release 2025-12-05.
- Location: Beamformer Analysis: Compare results.
- Observed content: The example compares resource and interval results and explains that interface bandwidth can limit gains from requested parallelism.
- Limit/counterevidence: Different HLS beamformer, not our RTL or a measured limit of this demo. Its numbers cannot become ours.
- Inspection: Root opened original.

## R07: Vivado native project archiving

- Source: [Vivado native project archiving](https://docs.amd.com/r/2025.2-English/ug835-vivado-tcl-commands/archive_project). AMD UG835, 2025.2, release 2025-11-20.
- Location: Description; Arguments; hook-script tip.
- Observed content: Native archiving packages required sources, constraints and run results. Optional settings and explicit inclusion of hook scripts affect archive contents.
- Limit/counterevidence: Archive existence is neither a passed-run assertion nor proof of what executed on the board. Packaging is already available.
- Inspection: Researcher checked; root independently opened original.

## R08: FuseSoC parameterized simulation/synthesis workflows

- Source: [FuseSoC parameterized simulation/synthesis workflows](https://fusesoc.readthedocs.io/en/stable/user/build_system/core_files.html). FuseSoC stable documentation labeled 2.4.7; publication date not displayed.
- Location: Filesets; Targets; Inheritance; Signed core files.
- Observed content: Core metadata describes file sets, dependencies, tops, tools, parameters and separate targets; documentation also covers signatures.
- Limit/counterevidence: Declared or signed metadata does not establish physical correctness. Parameterized reusable workflows are existing alternatives.
- Inspection: Researcher checked; root independently opened original.

## R09: Edalize build input and flow metadata

- Source: [Edalize build input and flow metadata](https://edalize.readthedocs.io/en/latest/edam/api.html). Edalize rolling latest EDAM documentation; publication date not displayed.
- Location: Introduction; File; Dependency; Flow options.
- Observed content: EDAM represents design inputs, parameters/options and dependencies, with distinct FPGA flow stages.
- Limit/counterevidence: Recipe metadata is not successful execution or bit-for-bit reproducibility. EDA orchestration already exists.
- Inspection: Researcher checked original; root did not independently refetch.

## R10: OpenTitan loaded artifact identity and mutable memory state

- Source: [OpenTitan loaded artifact identity and mutable memory state](https://opentitan.org/book/doc/getting_started/setup_fpga.html). lowRISC/OpenTitan rolling master documentation; publication date not displayed.
- Location: Automatic loading; custom bitstream; USR_ACCESS and Loading Bitstreams.
- Observed content: Its loader compares running-board and file identity metadata; the documentation explicitly warns that this does not establish later-programmed memory state.
- Limit/counterevidence: Specific OpenTitan boards/tools, not our KV260 integration. Loaded identity alone does not prove complete runtime state or output correctness.
- Inspection: Researcher checked; root independently opened identity section.

## R11: OpenTitan issue: source hashing can miss command-line dependencies

- Source: [OpenTitan issue: source hashing can miss command-line dependencies](https://github.com/lowRISC/opentitan/issues/31264). lowRISC/OpenTitan contributor issue, opened 2026-09-08; displayed open when checked.
- Location: Background, final paragraph.
- Observed content: The author warns that one source-file cache index omits the actual FuseSoC command line, potentially allowing reuse when rebuild was needed.
- Limit/counterevidence: Engineering concern/proposal, not demonstrated prevalence, measured loss or a failure SiliconeOS has prevented. Existing teams recognize and address provenance.
- Inspection: Researcher and root independently read original issue and date/state.

## R12: AMD native 32-bit loaded-design metadata

- Source: [AMD native 32-bit loaded-design metadata](https://docs.amd.com/r/en-US/ug570-ultrascale-configuration/USR_ACCESSE2). AMD UG570 revision 1.20.1, release 2025-03-04.
- Location: USR_ACCESSE2.
- Observed content: AMD documents a fabric-accessible 32-bit user value or timestamp associated with bitstream generation.
- Limit/counterevidence: Identifier is not a complete cryptographic receipt. No evidence our current design uses this primitive; no implementation change proposed.
- Inspection: Researcher checked original; root did not independently refetch.

## Leads excluded from the evidence

AMD 2025.2 Unrolling Loops URL could not be fetched by root; the accessible XD261 example was used instead. ACM artifact-policy direct fetch returned 403; no ACM badge or reproduction-certification claim is made. Search results and snippets were discovery leads, not substitutes for the opened originals. No broad market forecasts, labor-rate figures or new ROI totals were added.
