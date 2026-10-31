# DayOS solo-development and AI collaboration workflow

Status: Working agreement
Updated: 2026-10-31

## Roles

- User = Product Owner, UI acceptance, priorities, final PR merge decision.
- ChatGPT = Product manager, technical sounding board, requirement writer, independent reviewer.
- Claude Desktop Code = Implementation agent, code changes, local UI preview, tests, feature branches and PRs.
- GitHub = Single source of truth for requirements, decisions, implementation evidence and portfolio trail.

## One feature at a time

1. Discuss idea and intended user behavior with ChatGPT.
2. Create a GitHub Issue with context, requirements, acceptance criteria, exclusions and risks.
3. Claude reads Issue, relevant docs and CLAUDE.md; first proposes a short plan.
4. User approves plan; Claude implements in a feature branch. Keep PR focused.
5. Claude runs typecheck, lint, build and relevant tests; capture UI before/after evidence.
6. Claude creates PR linked to Issue. PR body lists scope, file changes, decisions, tests, screenshots, limitations and cost impact.
7. User sends PR link to ChatGPT; ChatGPT reviews actual code and risk, then drafts correction instructions.
8. Claude pushes fixes to the same PR. User checks UI and approves merge.
9. Update ADR, model or data registry when relevant; include in the same PR.
10. Record a short portfolio checkpoint only for meaningful milestones.

Use GitHub's `Closes #123` syntax in PR body when feature is complete and merging into default branch. Do not merge automatically.

## What to save

- Issue: final feature-level instruction and acceptance criteria, not every intermediary chat.
- PR: final implementation, test evidence, screenshot, what changed and why.
- ADR: important technical/product decision and alternatives.
- prompts/templates/: only reusable prompts, versioned with Git.
- CLAUDE.md: concise durable coding rules and relevant commands, not a long project diary.
- External model/data registries: versions, benchmark settings, dates, license, download location and cost.
- A private decision or idea that is not ready to build can live as a GitHub Issue labelled idea; no parallel backlog.

## Portfolio hygiene

Report only personally verified tests. Keep explicit distinctions between generated code, reviewed code and manually evaluated behavior. Exclude API keys, personal calendar/email data, local paths and raw proprietary files from committed docs.

## Suggested branch and PR naming

- `feat/<topic>`, `fix/<topic>`, `docs/<topic>`
- PR `feat: notification inbox with reminder logs`
- Every PR includes why, how verified, UI evidence, known limitation and issue link.

## Session handoff to Claude

"Read docs/PROJECT_INDEX.md, CLAUDE.md and Issue #N. Summarize existing code and propose a plan before coding. Keep this PR within the Issue acceptance criteria. Show tests and a UI preview. Do not push secrets or merge."
