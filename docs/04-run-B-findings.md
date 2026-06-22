# 04 — Run B Findings: Fully Local (Complete)

> **Status: pending.** This document will be completed once Run B (fully local, Ollama) finishes.
> The run is intentionally rate-limit-free and reproducible; because the local models are small and
> CPU/GPU-bound, the full ~1,000-call run takes several hours.

## Planned contents
- Setup: four local models (`llama3:8b`, `gemma2:2b`, `qwen2.5:3b`, `phi3`), 12 datapoints each.
- Completion table for all five phases (expected: all complete, no rate-limit losses).
- Full **four-model student ranking** with mean normalized scores.
- Judge-by-judge decomposition and judge-consistency (ICC / agreement) analysis.
- Teacher differentiation: which teachers produced the most discriminating questions.
- Comparison of structured-output validity rates across the local models.
- Embedded report screenshots from `coeval analyze all`.

Configuration: [`config/cybersecurity_local.yaml`](../config/cybersecurity_local.yaml).
