# DayOS data strategy

Status: Research candidates only; no datasets downloaded.
Updated: 2026-10-31

## Principle
Public calendar/dialogue data helps test language understanding, but does NOT represent user-specific recommendation preferences. Personalization requires consented first-party feedback.

## Candidate sources
| Source | Link | Purpose | Caveat |
|---|---|---|---|
| Microsoft SMCalFlow | https://github.com/microsoft/task_oriented_dialogue_as_dataflow_synthesis | Calendar intent and dialogue-to-action mapping | Check exact subset license, split and fit |
| ProAgentBench | https://arxiv.org/abs/2602.04482 | Proactive assistance evaluation | Large, privacy-sensitive artifacts; verify access and terms |
| Microsoft NL2API | https://github.com/microsoft/nl2api | Natural-language API selection | Validate current files and license |
| Google Taskmaster | https://github.com/google-research-datasets/Taskmaster | Task-oriented dialogues | Domain is broader than scheduling |
| Korea Time Use Survey | https://mdis.kostat.go.kr/ | Descriptive time-use research | No individual preference labels; access restrictions |
| American Time Use Survey | https://www.bls.gov/tus/datafiles.htm | Diary-based activity statistics | US survey, not individual calendar intent |

## Rules
- Record dataset version, release date, raw size, download date, checksum, license, source URL, preprocessing script, train/test split and known restrictions.
- No large automatic downloads; inspect files and storage requirements before user approval.
- Raw datasets and checkpoints live on approved external drive, not GitHub.
- No real user calendar, email or personal traces in public test data without explicit consent and scrubbing.
- Start with synthetic test scenarios; build evaluation before fine-tuning.
- Per-user event/task/suggestion/feedback/notification/action receipt schemas with RLS and retention/deletion mechanisms.

## Metrics
Calendar intent accuracy; suggestion Precision@3; actionable recommendation rate; false suggestion and unwanted notification rate; on-time and duplicate-free reminder delivery; approved agent task success; cost per action.

## Open
Licenses and exact dataset file sizes need verification before download. No data downloaded in this documentation PR.
