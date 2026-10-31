# DayOS: instructions for Claude Desktop Code

Read docs/PROJECT_INDEX.md and relevant Issue before coding.

- Product: user-controlled Calendar + Task planner. Never automatically reschedule.
- AI: on-demand recommendations by default; proactive future-event suggestions only by opt-in.
- Reminders: deterministic backend scheduling, timezone aware, duplicate-safe and separately configurable.
- Explicit user approval required before externally consequential actions.
- Web + PWA first. Keep backend and integrations separable for later Capacitor app.
- Implement one Issue per feature branch and focused PR. Never auto-merge.
- Propose a plan before coding, identify acceptance criteria, then show UI preview and test evidence.
- Store rationale in relevant ADR or PR; update the source docs when behavior changes.
- Never commit secrets, personal calendar/email, model weights or large datasets.
- Use external storage for large model/data assets only after mount, disk-space and license validation. Never silently fall back to internal disk.
- Check model exact revision, date, total/active parameters, benchmark conditions, hardware needs, license, API costs and DayOS-specific results before recommending a download.
- If information is unverified, mark it unknown rather than inventing it.
