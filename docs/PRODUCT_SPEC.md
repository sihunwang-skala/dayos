# DayOS product specification

Status: Draft v0.1
Updated: 2026-10-31

## Product goal

DayOS is a user-controlled, visually excellent calendar and daily planner with optional context-aware AI suggestions and, later, bounded task delegation.

## Non-negotiables

1. Users choose, place and modify events and tasks themselves. Do NOT implement automatic time blocking or unsolicited rescheduling.
2. AI recommendations are shown when requested by default. Proactive future-event suggestions are explicitly opt-in, quiet and dismissible.
3. Accurate reminders for user-defined deadlines are core. Separate deterministic reminders from optional AI recommendations.
4. Show only feasible AI-delegable work. Require authorization before externally consequential actions.
5. The calendar must remain useful if AI is disabled.
6. Users control notifications, privacy, data deletion and connected-account permissions.

## First release

- Responsive Today / Week view, quick event and task CRUD, labels, status and priority.
- Secure sign-in and per-user data storage.
- Backend-based reminders with time zones, idempotency, retries and delivery logs. Client tab need not remain open.
- In-app notification inbox plus one reliable delivery channel.
- On-demand suggestion button; future-event suggestions with explicit opt-in.
- Clear accept, reject, defer, dismiss and mute actions.

## Later

- Google Calendar sync, then optional Gmail / Notion integrations using minimum scopes.
- Approved AI execution with action receipt, run state, error handling and rollback where possible.
- Personalized recommendation ranking from consensually collected feedback.
- Web + PWA first, later iOS / Android via Capacitor if justified.

## Metrics

Weekly retention, tasks completed, reminder on-time performance, duplicate reminders, false interruptions, suggestion precision and acceptance rate, agent task success and operating cost.

## Open questions

Target audience, visual design, delivery channel, onboarding, suggested notification digest limits, first delegation use case and first production hosting plan.
