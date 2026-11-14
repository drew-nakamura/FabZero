# Working across coding tools

## One source of shared context

`AGENTS.md` contains stable team instructions. `STATUS.md` summarizes project state. `docs/spec/` holds the product contract when the spec workflow produces it. `tasks/<unique-id>.md` holds one task's ownership, evidence, and continuation checkpoint; start from `TASK_TEMPLATE.md`.

Use unique IDs, such as a coordinator-assigned `TASK-001` or a name-prefixed ID. Do not have several workers append to one progress log. Keep task records focused; keep large build logs in artifacts and link them. Do not create empty product specs just to satisfy a checklist.

On each task, reconcile the latest explicit human direction, saved decisions, current code, and test evidence. Report contradictions that affect scope or correctness. A status label cannot prove code works, and an agent's suggestion cannot become an accepted product decision on its own.

## Working before an agreed product spec

Shared agent behavior, project instructions, and bounded setup or discovery tasks can be defined through an explicit owner request before product requirements are settled. State the task's observable outcome and owned paths; do not invent a full spec as a prerequisite to improving the workflow. Existing exploratory drafts remain proposals, and accepted individual decisions do not imply approval of an entire build revision.

Use the "Build the smallest complete change" rules in root `AGENTS.md` for all project agents. They adapt useful ideas from [Ponytail's core instructions](https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail/SKILL.md): reuse working components, avoid speculative infrastructure, and preserve validation. We use our own project rules; no Ponytail plugin, lifecycle hooks, or additional agent runtime is required. Its published software benchmark is not evidence of RTL quality, Vivado performance, or KV260 readiness.

When defining a build agent, give it the relevant accepted task/requirements, inputs, expected deliverable, owned paths, allowed tools, dependencies, and a stopping condition. Require it to read the root guidance and return verification evidence plus unresolved limits. Keep each role focused; split it into separate workers only when there is independent work and clear ownership. Do not duplicate changing project rules in every role file.

For example, reuse a verified board wrapper and generate the selected component inside it, with independent behavioral checks and evidence for the required board execution. Do not make "simpler" mean replacing the required hardware result with CPU output or simulation. A proposed wrapper or platform is not verified merely because it is convenient.

## Supporting an owner who is new to coding with agents

The owner has explicitly asked every agent to help keep them within the agreed workflow and speak up immediately when the workflow or specs seem wrong. Explain unfamiliar steps in plain language and give a concrete next action. This preference applies across tool switches; do not infer the other student's experience from it.

When an issue appears, tell the owner as soon as you notice it, before taking a dependent action. Use a short explanation: what you observed, which requirement or workflow step it affects, what could happen, and the smallest way to get back on track. Label uncertainty and check it rather than presenting suspicion as a confirmed failure. Record a consequential unresolved issue and its recovery step in the task handoff.

For example, if asked to build from a draft spec, explain that the build scope has not been accepted and identify the specific revision or scope decision needed next. If two sessions are about to edit the same file, identify the ownership collision and arrange separate tasks or a stopped-writer transfer. If a handoff says tests passed but supplies no evidence, verify or label that result unverified before relying on it.

Pause only the action that depends on resolving the issue; continue useful work within existing authorization. Fix routine problems directly when the solution is already authorized. At meaningful stage changes, briefly state the current stage, agreed scope, and next step so the owner can stay oriented. Do not repeatedly ask for confirmation or repeat a warning that has already been resolved.

The workflow can change through an informed explicit human decision. Explain the consequences of a proposed deviation, recommend a practical correction or workflow adjustment, and record an accepted change in the affected spec/task/status files. Never silently drift from the workflow or treat an outdated procedure as more authoritative than the owner's current instruction.

## Starting in any tool

Open the actual repository/worktree root. Start a new session after changing bootstrap guidance, or explicitly request a re-read. A useful first prompt is:

```text
Read AGENTS.md and its startup references. Summarize the current spec status,
existing changes, and live task ownership. Then continue task <ID> within its
authorized scope and owned paths. Record evidence and a handoff before stopping.
```

Verify instruction loading once in each installed tool. Ask it to name the files it read, the current spec revision or its absence, and the ownership rule. Correct a wrong root or missing context before it edits. Installed versions and local/global settings have not been verified here.

- Codex: root `AGENTS.md` is the project entry point; check for applicable overrides if unexpected instructions appear. See [official instruction discovery](https://developers.openai.com/codex/guides/agents-md/).
- Claude Code: root `CLAUDE.md` contains the real `@AGENTS.md` import. This also covers sessions/versions without native AGENTS support and avoids Windows symlink requirements. See [official memory/import guidance](https://code.claude.com/docs/en/memory). Keep the import outside code fences.
- Cursor: use its native root `AGENTS.md` support. Existing `.cursor/agents/fabzero-spec.md` selects a specialized role; it is separate from shared rules. See [official rules documentation](https://cursor.com/docs/rules).
- Kiro: use its native root `AGENTS.md` support. If it generates `.kiro/specs/` artifacts, record how they map to the accepted `docs/spec/` revision; reconcile changes rather than creating a competing product contract. See [official steering documentation](https://kiro.dev/docs/steering/).

These entry points follow official documentation checked on 2026-11-13. Keep one canonical policy instead of copying it into four tools. Personal memory and session-resume features are supplemental; they do not transfer work to the other student or another tool.

## Parallel tasks

For a two-person hackathon, begin with two small, independent tasks. Extra sessions help only when ownership, interfaces, compute, and integration capacity support them. A UI task and a backend task can overlap only after their shared contract is agreed. Two tasks changing the same interface should be sequenced or have a single interface owner.

1. Name one integration owner. They maintain shared status and the live assignment list, settle overlapping claims, and integrate one change at a time. Tool preference does not elect a new integrator on every session start.
2. Give each task a bounded outcome, owned paths, acceptance criteria, dependencies, and resource reservations. Include ownership of high-contention files such as manifests, lockfiles, shared types, and build/project configuration.
3. Communicate assignments through a mutually visible channel: the same team conversation, an issue, a PR, or a coordinator-maintained board. Files in separate branches are snapshots, not a distributed lock. Independent task records reduce merge conflicts but cannot prevent two people claiming the same file.
4. Use one separate worktree and branch per writer on one machine; use separate clones/branches across the students' machines. Read-only review can happen alongside a writer. If writers must share a checkout, take turns and explicitly stop the outgoing writer before handing it over.
5. Before editing beyond your ownership, coordinate a transfer or let the shared-file owner make that change. If an unexpected live edit appears in your paths, preserve it, pause conflicting writes, compare the diff, and coordinate; do not restore an older copy.

Use `codex/` for Codex-created branches by default, with a unique task suffix. Other tools may follow the team's agreed branch naming. Always record the actual branch and base commit.

## Worktrees and uncommitted changes

Git worktrees provide separate working files, HEADs, and indexes while sharing the repository. They do not isolate external resources, ports, shared caches, or the FPGA board. See [Git's worktree documentation](https://git-scm.com/docs/git-worktree) and [Claude's parallel-worktree workflow](https://code.claude.com/docs/en/common-workflows#run-parallel-sessions-with-worktrees).

Before branching, inspect:

```powershell
git status --short
git branch --show-current
git rev-parse HEAD
git worktree list
```

A new worktree starts from committed content. It will not receive the main checkout's modified README, untracked instructions, local planning files, dependencies, or private environment settings. Get the intended setup onto an agreed baseline using the team's authorized review/commit process first, or explicitly transfer only the required files and record that dirty baseline. Never commit somebody else's work to make this convenient.

Example only, after agreeing the base branch, destination, and task; these commands were not executed by the setup task:

```powershell
git worktree add -b codex/TASK-001-ui ..\FabZero-worktrees\TASK-001-ui main
```

Replace the example ID and `main` if needed, and launch the coding tool in that new directory. Respect the tool's workspace permissions for the chosen destination. Do not use force flags to bypass a branch already in use. Do not switch the branch of a checkout another session is editing. Avoid concurrent repository-wide configuration or cleanup.

Each writer needs separate output directories and suitable environment setup. Reserve shared hardware, build runners, and any shared Vivado project/output path. Do not copy secrets into Git or task notes. Record the necessary environment variable names and setup steps without their values.

## Handoff or tool switch

1. The outgoing owner checkpoints its task record: purpose, requirement IDs, exact files and revisions, rationale, checks and failures, known limitations, processes still running, and the next executable action.
2. State whether the work is committed, uncommitted, untracked, or available only on one machine. A branch name or chat summary alone does not deliver uncommitted work. If providing a patch, account for new/untracked files separately and inspect it for secrets.
3. Stop the outgoing writer before transferring ownership. Do not leave an agent or process rewriting the receiver's files; explicitly identify any build processes allowed to continue.
4. The receiver acknowledges the transfer, reads shared instructions and the record, checks the actual path/branch/HEAD/status/diff, and verifies that required files and artifacts arrived. Do not infer ownership release from inactivity or an old timestamp.
5. Resume the next recorded action. Re-run checks when the code, environment, or baseline changed; do not blindly inherit a success claim from another checkout.

For the same task, switching Codex to Claude Code can reuse the existing worktree after the first writer has stopped. For a different task running concurrently, use a separate worktree. Across machines, share intended changes and task records through normal Git/review or a deliberate file transfer; local worktree paths are not portable handoffs.

## Integration and truthful completion

Task states: `proposed` -> `active` -> `ready` -> `done`. Use `blocked` with an owner and unblock condition; use `superseded` when requirements or assignments replace the work. A blocked task retains ownership until explicitly released.

The integration owner reviews the scoped diff and evidence, checks the task against the accepted revision, and integrates serially using the team's authorized process. Workers should stage only their owned files. Neither a task assignment nor this workflow automatically authorizes committing, pushing, merging, publishing, or board programming.

Resolve conflicts by understanding both intended behaviors and preserving unrelated work. Do not choose an entire side just to make Git quiet. Recheck interface compatibility and relevant acceptance criteria on the integrated result. If a spec revision changes, identify affected tasks and revise their scope before continuing incompatible implementation.

After integration, record the target revision, actual verification, remaining risks, and the next task in shared status. Mark `done` only when the task's acceptance criteria and relevant integrated checks are satisfied. Delay worktree/branch cleanup until intended changes and required artifacts are preserved and no writer or build still uses them.

For hardware, report each stage independently: simulation, synthesis, implementation/timing, bitstream generation, and board validation. Record actual tool/platform versions and evidence; never infer board success from generated RTL or a bitstream. Use small checks appropriate to documentation-only changes rather than launching FPGA builds.
