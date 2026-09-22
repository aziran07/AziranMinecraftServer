# Agent Working Agreement

These instructions apply throughout this repository.

## Responsibilities

- **Codex owns analysis, architecture, design, task decomposition, acceptance criteria, review, and independent verification.** Codex coordinates the work and reports the final outcome to the user.
- **Claude owns actual code implementation.** This includes application code, scripts, operational configuration, infrastructure changes, and automated test code, including fixes requested during review.
- Codex may inspect code, run commands and checks, and maintain design documents and agent instructions. Codex must delegate implementation to Claude instead of writing implementation patches itself.
- Claude must follow the agreed design and report ambiguities, blockers, and proposed design changes to Codex before implementing a materially different approach.

## Required Orca Workflow

1. Codex inspects the relevant repository state, identifies the root cause or requirements, and defines the design, scope, constraints, and observable acceptance criteria.
2. Read the installed `orca-cli` and `orchestration` skills and load their version-matched CLI guides before using Orca commands. Follow their executable discovery rules; do not guess commands or flags.
3. Use **Orca CLI** for Orca-managed worktrees and terminals, and **Orca orchestration** for task dispatch, threaded communication, questions, decisions, progress, and completion reporting between Codex and Claude. Use a Claude agent for implementation; a Codex worker is not a substitute.
4. Codex dispatches a bounded implementation task to Claude with the design, affected areas, acceptance criteria, validation expectations, and relevant context. Assign clear ownership when multiple tasks are active.
5. Claude implements the change, performs relevant local checks, and returns the changed files, implementation summary, validation results, and any remaining concerns through Orca orchestration.
6. Codex reviews the actual diff and independently runs the checks needed to verify the acceptance criteria. Claude's completion message alone is not verification.
7. Codex sends implementation defects back to Claude through Orca orchestration and repeats review and verification until the requirements are met.
8. Codex reports the final behavior, verification evidence, and unresolved limitations accurately. Keep task status consistent with the actual result.

Do not replace this workflow with built-in non-Orca subagents, untracked terminal handoffs, or self-implementation by Codex. If Orca or Claude is unavailable, report the concrete failure and stop implementation until the dependency is restored or the user explicitly changes the workflow. Independent analysis and documentation may continue.

## Never Conceal Bugs

- Fix the underlying cause. Do not introduce fallback paths, silent defaults, dummy data, no-op behavior, or success-shaped responses to make a defect appear resolved.
- Do not swallow exceptions, broadly catch and ignore errors, discard failed command statuses, or suppress diagnostics that expose a real failure.
- Do not use retries, alternate providers, compatibility branches, or degraded behavior to conceal broken assumptions, invalid configuration, missing dependencies, or implementation defects.
- Validate required inputs and configuration at the appropriate boundary. Surface failures with actionable context while keeping secrets out of logs.
- If recovery behavior is an explicit requirement, define the expected failure conditions and recovery semantics in the design. Make degraded operation observable and verify both the primary and recovery paths. Never report recovery as primary-path success.
- Do not weaken assertions, disable checks, skip failing tests, or change expected results merely to obtain a passing result. Changes to expected behavior require a justified design decision.
- Keep pre-existing failures visible and distinguish them from regressions introduced by the current work.

## Verification and Repository Care

- Define verification before implementation and choose checks appropriate to the change: focused tests, static checks, configuration validation, or runtime checks as needed.
- For bug fixes, reproduce the failure when feasible and verify that the change addresses its cause. Add meaningful regression coverage when appropriate.
- Report what actually ran and its outcome. Clearly identify checks that were blocked or not run; never claim unverified behavior works.
- Inspect the final diff for unintended changes and preserve unrelated user work.
- Protect credentials, server worlds, backups, and persistent service data. Do not include secrets or modify runtime data as an incidental part of a code change.
- Keep changes focused and avoid unrelated refactors or speculative abstractions.
