# Agent Working Agreement

These instructions apply throughout this repository.

## Responsibilities

- **Codex owns analysis, architecture, design, task decomposition, acceptance criteria, automated test authoring and maintenance, review, and independent verification.** Codex coordinates the work and reports the final outcome to the user.
- **Claude owns production implementation.** This includes application code, operational scripts, operational configuration, and infrastructure changes, including fixes requested during review. Claude runs tests and fixes implementation defects; Codex writes and modifies automated test code.
- Codex may inspect code, run commands and checks, write and maintain tests and test-only helpers or fixtures, and maintain design documents and agent instructions. Codex must delegate production implementation to Claude instead of writing production patches itself.
- Claude must report proposed test changes and their rationale to Codex through Orca orchestration. Codex reviews and makes warranted test changes; Claude must not modify tests or expected results to accommodate its implementation.
- Claude must follow the agreed design and report ambiguities, blockers, and proposed design changes to Codex before implementing a materially different approach.

## Required Orca Workflow

1. Codex inspects the relevant repository state, identifies the root cause or requirements, and defines the design, scope, constraints, and observable acceptance criteria.
2. This server is controlled over SSH by Orca running on another computer and uses the Orca relay at `~/.orca-relay/bin/orca`, not a local Orca installation. Read the installed `orca-cli` and `orchestration` skills and load their version-matched CLI guides through this relay; do not guess commands or flags.
3. Use **Orca CLI** for Orca-managed worktrees and terminals, and **Orca orchestration** for task dispatch, threaded communication, questions, decisions, progress, and completion reporting between Codex and Claude. Use a Claude agent for implementation; a Codex worker is not a substitute.
4. Codex defines verification before implementation, writes appropriate tests against the agreed requirements, and dispatches a bounded production implementation task to Claude with the design, affected areas, acceptance criteria, tests and validation expectations, and relevant context. Assign clear ownership when multiple tasks are active, including Codex ownership of test files.
5. Claude implements the production change, runs the relevant tests and local checks, and returns the changed files, implementation summary, validation results, and any remaining concerns through Orca orchestration. Claude reports test defects or missing coverage to Codex rather than editing tests itself.
6. Codex reviews the actual diff, adds or corrects tests as warranted by the agreed requirements, and independently runs the checks needed to verify the acceptance criteria. Claude's completion message alone is not verification.
7. Codex sends production implementation defects back to Claude through Orca orchestration, handles test defects itself, and repeats review and verification until the requirements are met. Changes to expected behavior require an explicit design decision, not merely a failing implementation.
8. Codex reports the final behavior, verification evidence, and unresolved limitations accurately. Keep task status consistent with the actual result.

Do not replace this workflow with built-in non-Orca subagents, untracked terminal handoffs, or production implementation by Codex. If Orca or Claude is unavailable, report the concrete failure and stop production implementation until the dependency is restored or the user explicitly changes the workflow. Independent analysis, documentation, test authoring, and verification may continue.

## Never Conceal Bugs

- Fix the underlying cause. Do not introduce fallback paths, silent defaults, dummy data, no-op behavior, or success-shaped responses to make a defect appear resolved.
- Do not swallow exceptions, broadly catch and ignore errors, discard failed command statuses, or suppress diagnostics that expose a real failure.
- Do not use retries, alternate providers, compatibility branches, or degraded behavior to conceal broken assumptions, invalid configuration, missing dependencies, or implementation defects.
- Validate required inputs and configuration at the appropriate boundary. Surface failures with actionable context while keeping secrets out of logs.
- If recovery behavior is an explicit requirement, define the expected failure conditions and recovery semantics in the design. Make degraded operation observable and verify both the primary and recovery paths. Never report recovery as primary-path success.
- Do not weaken assertions, disable checks, skip failing tests, or change expected results merely to obtain a passing result. Changes to expected behavior require a justified design decision.
- Keep pre-existing failures visible and distinguish them from regressions introduced by the current work.

## Code Simplicity and Readability

Synced from the global `~/.dotfiles/agents/AGENTS.md` on 2026-09-22. Its no-bug-concealment rules are covered by the section above.

- Write concise, straightforward code that humans can easily read and understand. Prioritize clarity over cleverness or brevity.
- Use descriptive names and explicit control flow. Avoid cryptic abbreviations, dense one-liners, and deeply nested logic.
- Keep functions focused and implementations as simple as the current requirements allow.
- Do not introduce excessive abstractions or unnecessary layers, wrappers, factories, or generic frameworks.
- Introduce abstractions only when they clearly simplify existing code or eliminate meaningful duplication. Do not design for hypothetical future requirements.
- Keep related logic together. Do not fragment straightforward behavior across many small functions or files without a clear readability benefit.

## Verification and Repository Care

- Define verification before implementation and choose checks appropriate to the change: focused tests, static checks, configuration validation, or runtime checks as needed.
- For bug fixes, reproduce the failure when feasible and verify that the change addresses its cause. Add meaningful regression coverage when appropriate.
- Report what actually ran and its outcome. Clearly identify checks that were blocked or not run; never claim unverified behavior works.
- Inspect the final diff for unintended changes and preserve unrelated user work.
- Protect credentials, server worlds, backups, and persistent service data. Do not include secrets or modify runtime data as an incidental part of a code change.
- Keep changes focused and avoid unrelated refactors or speculative abstractions.
