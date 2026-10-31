# DayOS model registry

Status: Candidate register, not an implementation or validated DayOS benchmark.
Updated: 2026-10-31

## Required metadata per evaluation
Provider / country, model identifier and immutable revision, announcement date, revision date, architecture (dense/MoE), total and active parameters, weight precision, quantization, model download size, context window, local RAM/VRAM need, inference hardware, public benchmark task / score / mode / prompt configuration, license, source URL, API price at recorded date, measured latency, DayOS-specific performance, and total expense.

Do not equate public scores in different reasoning modes or parameter count with memory demand.

## SKT A.X candidates
| Model | Approximate scale | Source | Notes |
|---|---|---|---|
| A.X 3.1 Light | 7B dense | https://huggingface.co/skt/A.X-3.1-Light | Exact version/release and license to confirm |
| A.X 4.0 Light | 7B dense | https://huggingface.co/skt/A.X-4.0-Light | Small local experiment candidate |
| A.X 4.0 | 72B dense | https://huggingface.co/skt/A.X-4.0 | Large memory requirement |
| A.X K1 | 519B total, 33B active MoE | https://huggingface.co/skt/A.X-K1 | Not laptop-class |
| A.X K2 | 688B total, 33B active MoE | https://huggingface.co/skt/A.X-K2 | Large FP8 checkpoint; no automatic download |

These sizes are preliminary sourced model-family characteristics and must be checked against the exact checkpoint's config/model card before use. Dates, context, measured scores, licenses and API prices remain unverified entries until separate review. Never invent them.

## Experiment record template
- Date and hardware:
- Model ID / revision:
- Release date and source:
- License:
- Weight size and required memory:
- Context window, precision and quantization:
- Benchmark name, version, split, language, prompting and thinking mode:
- Public results with source:
- DayOS test-set ID / scoring code commit:
- Accuracy / precision / false positives:
- p50/p95 latency and input/output token count:
- API cost or local hardware runtime cost:
- Observed failures and next decision:

## Storage rule
Store model weights, caches, processed datasets and large logs on a verified external volume only. If unavailable, refuse download rather than silently use Mac storage. Small scripts and metadata are versioned in Git.
