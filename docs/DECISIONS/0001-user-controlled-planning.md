# ADR-0001: User-controlled planning with optional AI assistance

Date: 2026-10-31
Status: Accepted as initial product direction

## Context

DayOS is not a Motion-style automatic time-blocking app. The user wants a visually good daily planner where they decide their own calendar, and where AI can propose relevant preparation tasks or future delegations without constant interruptions.

## Decision

- The user owns all event creation, time selection and changes.
- AI suggestions are on-demand by default.
- Proactive preparation suggestions are a separate opt-in mode, subject to limits, quiet hours, dismissal and feedback.
- Explicit reminders are deterministic scheduler jobs, independent of LLM recommendations.
- AI task execution is a later feature and requires bounded user authorization and an action receipt.

## Alternatives considered

- Always-on proactive AI: more discovery but risks notification fatigue and reduced control.
- Fully automatic schedule optimization: contrary to product intent.
- AI-only interface: weak day-to-day planner value if model unavailable.

## Consequences

We must separate scheduling data, reminder delivery, recommendation candidates, and action execution. Evaluate false interruptions and user preference alongside recommendation quality.

## Revisit when

Real-user feedback indicates that opt-in recommendations are not discoverable or that a better consent design improves adoption.
