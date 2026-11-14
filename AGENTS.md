# FabZero: instructions for every coding agent

## Project and team

- Two students are building FabZero for a hackathon. Preferred tools: Codex, then Claude Code, then Cursor, then Kiro. This is a tool preference, not permission to overwrite another contributor.
- The current direction is helping startups turn an idea into an FPGA demonstration without RTL expertise. A Kria KV260 is reported available; hardware readiness, customer, workload, stack, and final scope must be verified.
- Keep durable rules here. Keep changing progress in `docs/team/STATUS.md` and task handoffs in `docs/team/tasks/`. Do not rely on another tool's private chat history or memory.

## Help the project owner stay on track

- The project owner is new to coding with AI agents. Explain unfamiliar steps and commands in plain language: what they do, why they matter, and the next concrete action. Do not assume the other student has the same experience level.
- Immediately flag anything that appears wrong in the workflow or specs, including missing prerequisites, scope drift, conflicting ownership, stale handoffs, or unsupported success claims, even when the owner proposes the step. State the observation, distinguish facts from uncertainty, explain the consequence, and recommend the smallest correction.
- If the next action would skip required spec acceptance, conflict with another writer, or risk losing work, flag it before proceeding and pause only the affected action. Continue independent authorized work; handle routine fixes without unnecessary permission requests.
- At meaningful transitions, briefly identify the current stage, agreed scope, and next step. Help the owner follow the workflow without repeated warnings or jargon. If the workflow itself needs changing, explain why and propose an adjustment; honor an informed explicit change and update affected records.

## Start or resume every task

1. Read `README.md`, `docs/team/STATUS.md`, `docs/team/WORKFLOW.md`, and relevant task records. Check for more specific instructions in the directories you will edit.
2. Read `docs/spec/SPEC.md`, `docs/spec/DECISIONS.md`, and `docs/spec/HANDOFF.md` when present; consult the latest relevant review. Missing files mean the state is unestablished. Report consequential gaps; do not invent requirements, approvals, or progress.
3. Check `git status --short`, current branch, HEAD, and `git worktree list`. Inspect relevant existing changes before editing. A dirty file may belong to a teammate or another agent.
4. Identify the task's outcome, authorized scope, acceptance criteria, owner, branch/worktree, owned paths, and dependencies. Use `docs/team/TASK_TEMPLATE.md` for substantive tasks. Confirm live assignments with the coordinator when working in parallel; branch-local records alone cannot show other workers' claims.
5. Continue useful authorized work. Ask only for missing decisions that block it. Briefly state your task and important uncertainty before making changes.

## Specs and scope

- Project-wide working rules and reusable agent instructions can be improved before an agreed product spec exists. The user's explicit request authorizes bounded workflow/setup work; it does not silently approve a customer, feature, architecture, or hardware implementation. Saved exploratory drafts are discussion material until the founder accepts a build revision.
- `docs/spec/SPEC.md` defines product requirements; `DECISIONS.md` records accepted choices; the spec `HANDOFF.md` identifies the approved build revision. Team task records describe execution and do not grant product approval.
- Before product implementation, establish the accepted build scope from those files or the latest explicit human instruction. Never treat a draft, recommendation, or old handoff as approval. If a direct request changes scope, record that instruction and reconcile affected requirements.
- When explicitly acting as the spec agent, read `agents/fabzero-spec.md` and respect its planning-only role. Other agents should not automatically adopt that role. Preserve its explicit revision-acceptance workflow.
- Do not silently pick a customer, framework, interface, numerical target, or new feature. Label proposals and assumptions. Read project evidence and official technical documentation where needed.

## Build the smallest complete change

- Understand the requested outcome and read the affected code before editing. Trace callers, interfaces, configuration, and relevant checks so a small patch still completes the whole task.
- Prefer, in order: an existing project component or validated hardware integration; a standard platform feature; an already installed dependency; then the simplest new implementation that meets the task. Check compatibility and limitations rather than assuming reuse is safe.
- Add dependencies, abstractions, wrappers, settings, or additional agents only when a current requirement or concrete task justifies them. Do not build speculative infrastructure for later.
- Keep responsibilities as roles until separate agent contexts or services solve an actual coordination problem. Use ordinary software for deterministic execution, job state, timeouts, artifact collection, and retry limits.
- Propose a smaller scope when useful, explain what it would remove, and preserve the accepted outcome until the user accepts the change. Simplification is not permission to silently omit a requested behavior.
- Optimize for clear, maintainable, complete behavior rather than minimum line count. For hardware, preserve explicit interfaces, numeric semantics, clock/reset behavior, timing constraints, and reproducibility; shorter RTL alone is not an improvement.
- Never remove required input validation, meaningful error handling, security, accessibility, independent expected results, or acceptance evidence to make the implementation smaller. Generated candidates must not weaken the oracle or tests to pass.
- Run the smallest meaningful checks for the changed behavior. New nontrivial logic needs a focused check that can detect a wrong result. Reversible documentation or trivial changes do not need an invented test suite. Do not reduce established checks solely to save time.
- Keep simulation, synthesis, implementation/timing, bitstream creation, and board validation distinct. When physical FPGA execution is the agreed outcome, simulation or a prepared unrelated accelerator cannot substitute for it. Identify reused platform code, manual steps, and cached evidence truthfully.
- Record a deliberate shortcut only when it has a known limitation: describe the limit and the condition for revisiting it in the relevant code comment or task record. Do not add placeholder debt notes everywhere.
- In the handoff, state what changed, what was checked, what remains unverified, and any material limitation. Do not report model confidence as execution evidence.

## Parallel work and preservation

- Use one branch and one separate worktree/clone per concurrent writer. Switching branches inside a shared directory does not isolate edits. If isolation is unavailable, serialize writers; other sessions may review without writing.
- Split work by independently testable outcomes and owned paths. Agree shared interfaces first. One named integration owner coordinates overlapping files, shared status, merges, and shared resources such as the KV260.
- Stay within assigned paths. Coordinate ownership changes before editing a claimed file. Worktree isolation prevents local overwrites, not semantic conflicts or shared-device conflicts.
- Preserve unrelated tracked and untracked changes. Do not reset, clean, restore, stash, delete worktrees, force-push, or stage another worker's files as cleanup. Stage explicit paths if committing is authorized.
- Do not automatically commit, push, merge, publish, or program hardware unless the task already authorizes it. Never weaken permissions or store secrets in instructions or handoffs.

## Verify and hand off

- Discover actual build/test commands from project files; no product build or test command is established yet. Run checks appropriate to the change and record exact commands, results, environment, and relevant revision or dirty state.
- For FPGA work, distinguish simulation, synthesis, implementation/timing, bitstream generation, and board validation. A file's existence is not proof that any stage passed. Avoid crawling generated Vivado outputs without a task-specific reason.
- Before pausing, switching tools, or completing a task, update its record with changes, decisions, failures, blockers, exact next steps, and uncommitted/untracked files. Never claim unrun checks passed.
- The receiver must verify the actual diff and environment before continuing. The integration owner updates shared status and marks work done after integration and relevant verification. Use the detailed workflow for transfers and conflicts.

## Tool entry points

- This file is canonical for Codex, Cursor, and Kiro. `CLAUDE.md` imports it for Claude Code. Keep tool-specific adapters thin and do not duplicate changing project state.
- After changing guidance, re-read it or start a fresh session and verify which instructions loaded. These are instructions, not an automatic lock or enforcement system.
