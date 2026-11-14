# FabZero
CPVC x CPOCB x CPE AI Hackathon Nov 13-15

## Specification agent

The `fabzero-spec` agent helps specify FabZero itself before the build. Give it an idea and customer; it challenges the proposal, recommends changes, saves a working spec, and waits for your feedback. Repeat until you accept a revision for building.

Start in a Codex chat opened in this repository by pasting:

```text
Read agents/fabzero-spec.md and act as the FabZero spec agent in this conversation.
Idea: [your current idea]
Customer: [specific user or startup]
Constraints: KV260; [time left, team, installed tools, desired demo]
Run the first review round, save a draft when there is enough information, and wait for my feedback.
```

Or start a dedicated interactive Codex CLI conversation from PowerShell:

```powershell
Set-Location C:\Users\drewa\FabZero
.\scripts\start-spec-agent.ps1 -Idea 'Your idea' -Customer 'Your customer'
```

The launcher uses your configured model and permissions. It requires Codex CLI on `PATH` and your existing Codex sign-in. It enables web search for technical evidence. `-Preview` prints the initial prompt without launching Codex. `-Context` supplies optional constraints. Running without arguments resumes from saved planning files, or asks for the missing starting input; it starts a new conversation, not a CLI transcript resume. Use the CLI's `codex resume` picker to reopen the original conversation.

Continue naturally, for example:

```text
I agree with the customer objection. Narrow this to [customer]. Keep [constraint].
Revise the spec and attack the new version again.
```

Other useful requests: `Compare these directions`, `Show me the current spec`, `Are we ready?`, and `I accept revision N; finalize for building`.

Planning artifacts appear as the conversation develops:

- `docs/spec/SPEC.md`: the current draft, stable requirement IDs, acceptance criteria, assumptions, scope, and readiness.
- `docs/spec/DECISIONS.md`: accepted decisions, hypotheses, evidence, and superseded choices.
- `docs/spec/reviews/round-NNN.md`: the critique and result of each substantive round.
- `docs/spec/HANDOFF.md`: the accepted revision and build-agent assignments, created after explicit acceptance.

Builders should read the accepted spec and handoff together. Drafts are not implementation authorization. A material scope change returns the spec to draft and supersedes an older handoff.

The canonical instructions live in `agents/fabzero-spec.md`. Cursor can use `.cursor/agents/fabzero-spec.md`. The native Codex definition is `agents/fabzero-spec.toml`, installed as `.codex/agents/fabzero-spec.toml`; in a session that discovers it, ask `Use the fabzero-spec agent to review this idea and customer`. If named discovery is unavailable in your session, use the direct chat prompt or launcher above.

This is a custom spec workflow informed by ECC's planner and verification patterns. ECC installation and additional API keys are not required. It does not run implementation, synthesis, or board programming.
