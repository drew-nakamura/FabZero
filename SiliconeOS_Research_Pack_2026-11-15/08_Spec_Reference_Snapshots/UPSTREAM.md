# Scope sources and precedence

## Accepted demo route (D-025)

November 14, 2026: the selected demonstration uses a local application, JTAG + xsdb on KV260, and [result files](BOARD_RESULT_FILE.md). Both N=8 one-lane and four-lane artifacts require their own board verification. The presentation uses labeled recordings/screenshots of genuine runs. Linux and a website upload endpoint are outside the current route. Application design remains with the application owner; hash serialization and parent-run linkage still need agreement. See [decisions](DECISIONS.md).

Recorded November 14, 2026 (America/Los_Angeles).

## Current source: teammate email

The founder corrected the source from GitHub to the emailed DEMO_PRODUCT_AND_FPGA_SPEC.md and requested updating our specs/context to the new direction. The imported [revision 1.0](DEMO_PRODUCT_AND_FPGA_SPEC.md) is byte-for-byte the file supplied from Downloads. SHA-256: `e0882902bb3dc645b4c90830745f8e642e213372981386ea871a373d38033e1c`.

The attachment remains byte-identical. D-025 explicitly supersedes its website endpoint and unspecified runtime/presentation route: use the local application, JTAG/xsdb, result files and genuine recorded presentation. Its embedded commands and scope-frozen label do not prove implementation or authorize new execution in this documentation task.

Read [SPEC.md](SPEC.md), [DECISIONS.md](DECISIONS.md) and [HANDOFF.md](HANDOFF.md) alongside it for reconciliations: current SiliconeOS spelling, proven diagnostic JTAG baseline, matmul-specific pending evidence, and schema details needing joint agreement. The unchanged source retains SiliconOS spelling and its older blanket hardware-unverified statement.

## Pinned GitHub source and publication state

Remote: [drew-nakamura/FabZero](https://github.com/drew-nakamura/FabZero). The earlier investigation fetched these objects. A read-only `git ls-remote --heads origin` check on November 14 reconfirmed the four published tips below; this synchronization performs no fetch/push. Listed tip commit dates are not upload times; no GitHub push-event history was obtained.

- `drew-branch`: c192cc330c2a89718db1dba5625a66ff08349b0d, November 14 at 11:54:33 Pacific, our diagnostic bring-up publication.
- `codex/ai-rtl-generation`: b8d9fca181acf007d96e8c15ecb298b944dab8b4, November 14 at 11:24:02 Pacific, newest teammate branch by tip commit date.
- `codex/siliconos-demo`: 84fcae1000f056f869b6b84a28804b98cb7b6a48, November 13 at 20:32:08 Pacific, older app branch.
- `main`: 5ea8480d34980210b42d83279d1e45475c99af19, initial commit.

Local drew-branch is now aa19ae5488ed24435eca03aade87333744398f18 (report tools), ahead of its published c192cc3 tip. This revision-8.2 documentation and simulation-evidence mirror is uncommitted in both checkouts; it is not on GitHub. The teammate application remains unmerged.

Read-only review used immutable Git blobs at b8d9fca181acf007d96e8c15ecb298b944dab8b4:

- [Large strategy/execution plan](https://github.com/drew-nakamura/FabZero/blob/b8d9fca181acf007d96e8c15ecb298b944dab8b4/SILICONOS_PLAN.md).
- [Delivery contract](https://github.com/drew-nakamura/FabZero/blob/b8d9fca181acf007d96e8c15ecb298b944dab8b4/docs/SPEC_AND_DELIVERY_CONTRACT.md).
- [FPGA gameplan](https://github.com/drew-nakamura/FabZero/blob/b8d9fca181acf007d96e8c15ecb298b944dab8b4/docs/PARTNER_FPGA_GAMEPLAN.md) and [RTL/AXI contract](https://github.com/drew-nakamura/FabZero/blob/b8d9fca181acf007d96e8c15ecb298b944dab8b4/hardware/BRINGUP.md).
- [Build/QA status](https://github.com/drew-nakamura/FabZero/blob/b8d9fca181acf007d96e8c15ecb298b944dab8b4/docs/BUILD_STATUS.md), [README](https://github.com/drew-nakamura/FabZero/blob/b8d9fca181acf007d96e8c15ecb298b944dab8b4/README.md) and [generated RTL contract](https://github.com/drew-nakamura/FabZero/blob/b8d9fca181acf007d96e8c15ecb298b944dab8b4/docs/AI_RTL_GENERATION.md).
- [Customer/demo plan](https://github.com/drew-nakamura/FabZero/blob/b8d9fca181acf007d96e8c15ecb298b944dab8b4/docs/DEMO_AND_CUSTOMER_PILOT.md) and [judging readiness](https://github.com/drew-nakamura/FabZero/blob/b8d9fca181acf007d96e8c15ecb298b944dab8b4/docs/JUDGING_READINESS.md).
- [ASIC exploration](https://github.com/drew-nakamura/FabZero/blob/b8d9fca181acf007d96e8c15ecb298b944dab8b4/docs/ASIC_WORKFLOW.md) and [IP shortlist](https://github.com/drew-nakamura/FabZero/blob/b8d9fca181acf007d96e8c15ecb298b944dab8b4/docs/RTL_IP_SHORTLIST.md).

Earlier plan text proposed Next.js, SSH/Linux and a same-resource optimization. Later app/contracts and the email refine that: existing plain-JavaScript/Python app, confirmed local loading route, catalog path primary, capacity comparison rather than a demonstrated same-resource optimization. Do not implement every older proposal as a frozen requirement.

## Local evidence and history

[Bring-up README](../../hw/bringup/README.md), published at c192cc330c2a89718db1dba5625a66ff08349b0d, and its local task record describe console/PL success with the diagnostic core. They establish a different artifact from matmul. The later [native XSIM evidence](../verification/matmul-xsim-2026-11-14/README.md) records all eight directed lifecycle/AXI tests passed with unchanged pinned RTL/testbenches. This synchronization copies their accepted logs/manifests without rerunning them. Matmul physical acceptance remains separate. The active pinned checked-in-RTL integration pilot does not yet have its accepted parent archive.

Preserved earlier research: [SPEC revision 7](SPEC-revision-007.md), [architecture revision 7](ARCHITECTURE-revision-007.md), [camera demo revision 1](../demo/DEMO-camera-revision-001.md), earlier decisions/reviews and the historical research brief. The spec and architecture archives are unchanged; the camera archive labels one source-checkout-only report reference as a plain path, with its original retained locally. Archives remain alongside the original directories so other relative references keep working. They are historical, not current navigation entry points. Existing research sources remain background evidence, not current workload requirements.
