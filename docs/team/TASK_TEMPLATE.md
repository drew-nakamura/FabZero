# <unique task ID>: <observable outcome>

- Status: proposed | active | blocked | ready | done | superseded
- Updated: <date/time with timezone>
- Owner: <student + tool/session identifier; one writer>
- Integration owner: <name/session>
- Repository/worktree path: <actual path>
- Branch and base commit: <branch; full base SHA>
- Current HEAD: <full SHA; identify dirty work separately>
- Scope authority: <accepted spec revision and requirement/acceptance IDs, or explicit human request>
- Owned paths: <specific files/directories, including this record>
- Shared resources: <board/build runner/ports; reservation or none>
- Dependencies: <task IDs, interface/version, or none>
- Acceptance criteria: <observable pass/fail conditions>

## Plan and contracts

<Small steps; shared inputs/outputs, types, formats, and error behavior agreed before parallel implementation.>

## Progress and decisions

<Implemented versus proposed; decision sources; files changed; unresolved assumptions.>

## Verification evidence

- Command/check: <exact command and working directory>
- Environment: <relevant tool/platform versions>
- Revision/state tested: <SHA plus relevant uncommitted changes>
- Result: <pass/fail/not run and reason; logs/artifact paths>

## Transfer checkpoint

- Commits/PR or patch: <exact references; say explicitly if none>
- Uncommitted/untracked files: <explicit paths and how the receiver gets them>
- In-progress processes: <session/job, logs, outputs, stop/resume instructions; or none>
- Blockers/risks: <what remains and who can resolve it>
- Next steps: <ordered, executable continuation>
- Ownership transfer: <old owner stopped writing; intended receiver; receiver acknowledgment or pending>
- Integration: <not integrated, or target SHA and verification result>

Do not copy placeholders into factual claims. `ready` means handed off for integration; `done` requires integration and relevant verification. A blocked owner retains the claim until it is explicitly released or transferred.
