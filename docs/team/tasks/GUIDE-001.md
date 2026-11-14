# GUIDE-001: shared simplicity and verification rules

- Status: ready (guidance applied and checked locally; publication pending)
- Updated: 2026-11-14 (America/Los_Angeles)
- Owner and bounded integration owner: Codex, Assess ECC for FPGA startup workflow chat, acting on Drew's explicit request.
- Source checkout: `C:\Users\drewa\FabZero`; branch `main`; base/HEAD `5ea8480d34980210b42d83279d1e45475c99af19`, with pre-existing local work.
- Publication checkout: `C:\Users\drewa\FabZero-worktrees\drew-branch`; starting HEAD `cdfaeaaf9aa8ca2b59f4e7e9c96ceb60c7db10c1`.
- Scope authority: add useful Ponytail principles to project/build-agent guidance without requiring an agreed product spec; prior instruction to publish this workflow work on `drew-branch`.
- Owned edits: root `AGENTS.md`, the shared-guidance section in `README.md`, `docs/team/WORKFLOW.md`, `docs/team/STATUS.md`, and this record. Preserve existing guidance while integrating the new rules.
- Supporting publication files: existing `CLAUDE.md` import and `docs/team/TASK_TEMPLATE.md`, needed by the shared startup references. Keep their content unchanged.
- Excluded paths: `docs/spec/` and other chats' task records. No hardware, product implementation, external installation, new worker, or tool-permission change.
- Acceptance: common rules work before spec agreement; preserve accepted outcomes/verification; explain how future agents inherit them; reconcile stale status; validate references and publish the scoped guidance on drew-branch.

## Changes and rationale

- Canonical rules live in root `AGENTS.md`; existing Claude import and native project entry points remain thin. No plugin or duplicate per-tool policy is added.
- Added reuse-first, bounded-scope, ordinary-controller, clear-code, meaningful-check, honest-shortcut, and evidence-handoff rules.
- Protected independent expected results, numeric/interface/clock/reset semantics, required timing/board evidence, and requested behavior against inappropriate simplification.
- Distinguished authorized setup work from product implementation. The founder says no agreed spec exists; exploratory files remain preserved discussion material.
- The earlier shared-guidance task states that no writer continues after it ends. This task adopts only the explicitly requested shared-guidance edits; the live spec chat's paths remain untouched.

## Verification and checkpoint

- Initial checks: source Git status/HEAD/worktrees and active chat inventory inspected. Publication worktree was clean at the recorded HEAD.
- Git reads outside the source sandbox required execution as the repository owner; no global safe-directory exception was added.
- Documentation checks passed across seven guidance files: six local Markdown links resolve, no trailing whitespace, Claude import remains exactly `@AGENTS.md`, and no spec handoff is present. `git diff --check` passed for tracked changes.
- Pending: scoped publication diff inspection and drew-branch remote verification.
- No product test, FPGA build, or board action is appropriate for this instruction-only change.
- Current work exists locally; commit and publication evidence will be recorded after checks. No new background writer was started.
