# FabZero shared status

Snapshot date: 2026-11-14 (America/Los_Angeles). Recheck files and Git before relying on this snapshot.

## Confirmed context

- Team: two students. Tool preference: Codex, Claude Code, Cursor, Kiro.
- The project owner is new to coding with agents and asks for plain-language guidance, immediate workflow/spec issue flags, and help staying within the agreed workflow. The shared instructions and workflow record this preference for every tool.
- Direction: help startups move from an idea to an FPGA demonstration without RTL expertise. The owner confirms there is no agreed product spec yet. Exploratory drafts and individual decisions are saved under `docs/spec/`; read those directly for the latest discussion rather than treating this summary as product approval.
- Project-wide working rules are independent of product requirements. The owner authorized adapting Ponytail's useful principles into the shared instructions: reuse working components, avoid speculative complexity, and preserve meaningful verification. This is workflow setup, not permission to start product implementation.
- A Kria KV260 is reported available. Access, boot, toolchain, licenses, and working hardware baseline are unverified.
- README event label: CPVC x CPOCB x CPE AI Hackathon Nov 13-15. Confirm the actual deadline and remaining time before scheduling scope.

## Repository evidence

- Source checkout: `C:\Users\drewa\FabZero`, still on `main` at initial commit `5ea8480d34980210b42d83279d1e45475c99af19`, with local guidance and planning changes. Preserve other chats' files.
- Separate publication worktree: `C:\Users\drewa\FabZero-worktrees\drew-branch`, inspected clean at `cdfaeaaf9aa8ca2b59f4e7e9c96ceb60c7db10c1` before this guidance update. The spec-agent setup was published on that branch; `main` was not changed. See `tasks/GIT-001.md` for verified publication evidence.
- Spec-agent checks previously completed: native TOML validation and installed/source comparison, launcher preview, and an independent one-round behavioral dry run. A full interactive launcher session and hardware flow were not tested by those checks.
- Exploratory `docs/spec/SPEC.md`, `DECISIONS.md`, reviews, research, and a spec task record exist in the source checkout. Latest inspected draft was revision 4; this is a changing conversation snapshot, not an agreed build spec. No approved `HANDOFF.md` was present when checked for this update.
- Local project folders do not establish a working hardware design. No product implementation or hardware-stage success is asserted by this guidance update.
- Local modified/untracked guidance and spec files are not automatically available in a fresh clone or separate worktree. Share only the intended files through the authorized branch workflow.

## Coordination and work

- Integration owner: not yet assigned. Choose one of the students or one active agent before concurrent implementation/integration.
- `tasks/TEAM-001.md`: shared guidance and handoff setup, ready locally; no commit or merge performed.
- `tasks/GIT-001.md`: completed publication of the spec-agent setup on `drew-branch`.
- `tasks/GUIDE-001.md`: adoption of the project-wide simplicity and verification rules; its checkpoint records checks and publication state.
- The spec chat owns `docs/spec/` and remains independent of this guidance change. This task does not edit its drafts, reviews, research, or accepted decisions. Confirm live assignments before parallel editing.
- Shared KV260/build-runner ownership: unassigned; reserve actual shared resources before use.

## Next steps

1. Carry the shared working guidance into future sessions and build-agent definitions; re-read root `AGENTS.md` after these changes. Keep publication on `drew-branch` per the owner's instruction and preserve the source checkout's separate planning work.
2. Continue the existing spec workflow. There is no agreed product spec yet; retain exploratory material without treating it as implementation approval.
3. After accepting a build revision, appoint the integrator and assign independently testable tasks with paths, interface contracts, and verification criteria.

The integration owner maintains this summary at milestones. Workers update their individual task records. Saved status can be stale; current code, checks, and explicit human decisions must be reconciled.
