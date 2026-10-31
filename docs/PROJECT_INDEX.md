# DayOS project index

Status: planning, not yet implemented
Updated: 2026-10-31

## Source of truth

- [PRODUCT_SPEC.md](PRODUCT_SPEC.md): what DayOS must do, and what it must not do.
- [WORKFLOW.md](WORKFLOW.md): ChatGPT, Claude Desktop, GitHub handoff and review.
- [DECISIONS/0001-user-controlled-planning.md](DECISIONS/0001-user-controlled-planning.md): decision rationale.
- [DATA_STRATEGY.md](DATA_STRATEGY.md): data candidates, privacy and evaluation.
- [MODEL_REGISTRY.md](MODEL_REGISTRY.md): model comparison and experiment metadata.
- [CLAUDE.md](../CLAUDE.md): short implementation rules automatically read by Claude Code.
- [Prompt template](../prompts/templates/implement-feature.md): reusable, not all raw chat history.

## Workflow links

Idea -> GitHub Issue -> implementation plan -> Claude feature branch -> PR with tests, screenshots and decisions -> ChatGPT review -> user approval -> merge.

GitHub Issues hold actionable requirements and acceptance criteria. PRs hold evidence of implemented work. ADRs hold durable reasons for decisions. Avoid separate, conflicting task lists in Notion or chats.

## How to recover context after weeks

1. Read this index and PRODUCT_SPEC.
2. Look at open GitHub Issues and PRs, then recent merged PRs.
3. Read relevant ADR and MODEL_REGISTRY or DATA_STRATEGY entries.
4. Ask ChatGPT to review a specific Issue/PR link rather than paste the whole codebase.

## Documentation freshness rule

When a feature materially changes the product behavior, update its Issue / PR and the affected reference document in the same PR. When a trade-off changes, supersede rather than silently erase an ADR. Keep project status and unresolved questions accurate.

## Portfolio checkpoints

For each shipped feature, preserve: problem statement, UI screenshot or demo, architecture choice, PR link, tests, measured outcomes, limitations and what the owner learned.
