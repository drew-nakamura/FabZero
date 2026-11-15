# SiliconeOS scope and integration handoff

Updated November 14, 2026 (America/Los_Angeles). Baseline: [SPEC revision 8.2](SPEC.md), [D-025](DECISIONS.md), the unchanged [email revision 1.0](DEMO_PRODUCT_AND_FPGA_SPEC.md), and [source ledger](UPSTREAM.md). This handoff records current decisions and evidence; it is not a completion certificate.

## Selected route and responsibilities

D-025 selects a local application, JTAG + xsdb, [result files](BOARD_RESULT_FILE.md), separate N=8 one-/four-lane board artifacts, and labeled recordings/screenshots of genuine runs. No Linux image or website upload endpoint is required. The application owner retains audience-facing design; the existing local Python/JavaScript stack does not need a framework or native-GUI rewrite merely to meet this decision.

The application owner handles controls, optional AI, catalog, simulation/oracle, export, local physical-result validation/import/rendering, stale/evidence labels and customer/rehearsal work. The hardware owner handles pinned RTL integration, wrapper, implementation, fixed runner and physical evidence. An overall integration owner and live board session still need explicit coordination. Preserve the verified [diagnostic bring-up](../../hw/bringup/README.md).

## Completed evidence and active work

- Diagnostic bring-up, published at c192cc330c2a89718db1dba5625a66ff08349b0d: console, synthesis, implementation/timing, bitstream and physical `3x+1` readback, repeated after power cycle. Vivado/xsdb 2025.2; xck26-sfvc784-2LV-c; board part xilinx.com:kv260_som:part0:1.4. This is platform evidence, not matmul evidence.
- [Eight directed XSIM simulations](../verification/matmul-xsim-2026-11-14/README.md) passed at pinned teammate b8d9fca181acf007d96e8c15ecb298b944dab8b4: lifecycle and AXI tests for N=8/16, LANES=1/4. RTL/testbenches unchanged; explicit `-timescale "1ns/1ps"` resolves the earlier default-timescale elaboration failure. This is not a rerun of the application's Icarus random regression or a board test.
- Report-summary tools are committed locally on drew-branch aa19ae5488ed24435eca03aade87333744398f18. Their recorded seven focused checks and OOC synthesis observations are separate from completed implementation or physical measurements. Power remains an estimate where vectorless activity is used.
- The matmul board integration/build pilot is active on pinned checked-in RTL in `hw/matmul_board/`. It prepares separate one-/four-lane builds and the runner. No completed implementation/timing, bitstream or matmul board correctness is asserted here; obtain current artifacts and stage-specific reports from the active hardware owner.

## Source intake and the pilot boundary

The pilot uses unchanged checked-in `matmul.sv` and `matmul_axi.sv`; their exact hashes are in the simulation [source manifest](../verification/matmul-xsim-2026-11-14/source_manifest.json). The two files are identical at inspected 84fcae1000f056f869b6b84a28804b98cb7b6a48 and b8d9fca181acf007d96e8c15ecb298b944dab8b4. This does not establish compatibility with a later generated candidate.

An accepted parent run/handoff ZIP is still outstanding. It does not block the explicitly authorized checked-in-RTL pilot. Before archived-vector tests and an end-to-end receipt claim, obtain the actual parent ID, supported parameters, exact source/test snapshots and hashes, independent inputs/expected outputs, cycle semantics, trusted monitor where applicable, wrapper/dependencies and agreed result schema. Pin the exported candidate itself; a current branch file may differ. Integration aids in a ZIP are separately unverified for its archived candidate.

## Remaining physical gates

1. The hardware owner completes the pilot's board integration and full implementation. Review actual clock/reset/AXI/address mapping, setup/hold/pulse width, DRC, methodology and unconstrained paths. Record actual clock and address allocation, reports, source/build hashes, bitstream, XSA and initialization files. OOC synthesis cannot satisfy this gate. Build the four-lane artifact separately after one lane meets timing; board-run ordering remains one lane first.
2. Prepare and check the fixed xsdb runner offline, including a deliberately wrong expected output and failed-run serialization. Preparing a runner is distinct from authorizing or executing a board session.
3. In a separately coordinated board session, require interface ID 0x53494c01, compiled N=8/LANES=1, and address-register write 5/read 5/clear/read 0. Use the new build's actual map, never an assumed diagnostic address.
4. Load identity A and B[i]=i-32; start; wait with a finite timeout for `(status & 3)==2`; read all 64 signed outputs and the completed cycle counter. Require every expected output and 512 compute clocks. Repeat without reload and reset/reload/rerun. Then exercise the exact accepted archived vectors against the independent oracle.
5. Write a new immutable result folder and implementation manifest per BOARD_RESULT_FILE.md. Preserve failed attempts and distinguish programming, host transfer/polling/readback and accelerator busy time. Do not edit the parent simulation report or infer board availability from old results.
6. After one-lane physical success, identify and test the separate four-lane artifact with the same inputs; require 128 checked-in compute clocks, repeated/reset checks, its own manifest and result. N=16 software coverage does not establish N=16 board validation.
7. The application independently validates/imports both physical results as separate evidence, preserves immutable parent linkage and exports the receipt. Capture labeled recordings/screenshots with run IDs; rehearse under four minutes. One physical artifact or simulation-only output remains a disclosed reduced outcome.

## Shared contract details still open

- Agree BOARD_RESULT_FILE.md's proposed hash serialization, source-file keys, parent linkage and selected-run retention before either side relies on them. Preserve verified runtime/source/input/output identity across both sides.
- Agree implementation-manifest content, transfer and report verification. A manifest hash or `timing_met` flag alone does not prove timing passed or bind a result to the programmed artifact.
- Keep logical top `matmul_axi` distinct from the actual board HDL top. A generic interface ID and compiled N/LANES do not replace artifact/source hashes.
- Use truthful JTAG runtime values: no OS kernel is running; `kernel_version` is null under the file contract. No invented Linux identity.
- Agree replay/idempotency and schema compatibility for local import. The application must recompute outputs and hashes, reject invalid evidence, preserve failures, and keep resources unknown without bound implementation reports.

No application API key is needed to integrate supplied checked-in RTL. Completed diagnostic bring-up and directed simulations do not need repeating solely because older handoffs predate them; recheck when source, environment or the tested behavior changes. This documentation synchronization ran no simulation, build or board command and made no source merge, commit or push.
