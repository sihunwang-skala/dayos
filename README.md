# DayOS

[English](README.md) | [한국어](README.ko.md)

**Context-Aware Personalized AI Planner**

A web-based planner that, on request, turns your own schedule and preferences into personalized preparation and next-step suggestions.

> **Status:** Planning and design phase. No application code yet. Everything below describes goals, not shipped features.

## Product Vision

- **You build your own schedule.** Events are created and edited by the user.
- **Personalized.** Suggestions use your schedule, preferences, priorities, and past feedback.
- **AI only when you ask.** Nothing is recommended unless you request it. Reminders run on plain rules, without AI.
- **Proposals are separate from actions.** The AI only proposes. Only what you approve is applied, and every applied change is logged.
- **Privacy.** Per-user data isolation, deletion support, and consent before any data goes to an external model.

## High-level Architecture

```text
Browser (web app)
   │
App server ── auth / per-user data isolation
   ├─ Calendar service        user-only writes
   ├─ Reminder service        rule-based, no AI
   └─ AI recommendation       on request only
         ├─ Consent gate      before any external call
         ├─ Proposals         AI output is stored here only
         ├─ Execution log     approved changes and their results
         └─ Model layer       model-agnostic adapters (cloud / local)
```

A concept-level diagram. Implementation details, internal personalization logic, and evaluation data are not part of the public documentation.

## Concept UI Preview

> **These are concept mockups, not screenshots of a working product.** All data is fictional and no application code exists yet.

A single static HTML page with an English / Korean language switch: [`docs/concept/index.html`](docs/concept/index.html) (open it in a browser).

| Screen | What it shows |
|---|---|
| 1. Calendar | A user-managed schedule and preferences; no AI call until you request one |
| 2. Before sending | Exactly what will be sent to the model, and a consent step |
| 3. Suggestions | Proposal cards with accept / reject, and an execution log |

![Concept 1: Calendar](docs/assets/concept-calendar.en.png)
![Concept 2: Before sending](docs/assets/concept-consent.en.png)
![Concept 3: Suggestions](docs/assets/concept-proposal.en.png)

### Walkthrough video

A short walkthrough of the concept mockup with Korean captions. It is generated from the mockup, not a screen recording of a real product.

![Walkthrough (Korean captions)](docs/assets/dayos-concept-walkthrough.ko.gif)

[Download MP4 (Korean captions)](docs/assets/dayos-concept-walkthrough.ko.mp4)

## Project Status

| Area | Status |
|---|---|
| Product definition | Draft complete |
| Architecture | Draft complete |
| Concept UI | Mockup only |
| Application code | Not started |

## Copyright & Usage

Copyright © 2026 Sihun Wang. All Rights Reserved.

This project is publicly available for viewing and portfolio demonstration purposes.

All rights to the original source code, documentation, designs, and project-specific assets are reserved by the author.

No permission is granted to reproduce, modify, redistribute, or commercially use the original materials without prior written authorization, except as permitted by applicable law or GitHub's Terms of Service.

Third-party libraries, dependencies, and other externally sourced materials remain subject to their respective licenses and ownership rights.

For licensing, collaboration, or commercial inquiries, please contact the repository owner.
