# 05 — Conclusions

> **Status: partial.** Cross-run comparative conclusions will be finalized after Run B. The
> conclusions already supported by Run A are recorded below.

## Conclusions established so far (from Run A)

1. **CoEval's automatic provisioning works on a real technical domain.** With only a one-paragraph
   task description, the framework inferred a sensible cybersecurity attribute space (network, web,
   crypto, malware, defense; difficulty tiers) and a 19-factor rubric aligned with expert judgment
   criteria. No manual benchmark design was required.

2. **Individual LLM judges are biased; the ensemble is the point.** Judges differed sharply in
   strictness (score gap 0.26 vs 0.02 for the same answers) and showed self-preference. Averaging
   across a diverse judge panel preserved the correct consensus ranking — empirically validating the
   framework's core design rationale.

3. **Free cloud LLM tiers do not scale to ensemble evaluation.** OpenRouter's 50-requests/day
   account cap makes a ~1,000-call run impossible on the free tier. Reproducible ensemble evaluation
   therefore favors **local inference** (Ollama) or a funded API budget.

4. **Structured-output reliability is a real axis of model quality.** Only 51% of judgments were
   well-formed JSON in Run A, with smaller models contributing most of the failures. A model's
   ability to act as a reliable *judge* is distinct from its ability to be a strong *student*.

## Conclusions added after Run B

5. **CoEval delivers a complete, reproducible ranking on commodity hardware.** Run B finished all
   five phases fully locally (no API budget, no cloud) with a 99% judgment-validity rate, producing
   the ordering phi3 > llama3-8b > qwen2.5-3b > gemma2-2b.
6. **Model scale is not destiny.** The 3.8B `phi3` outscored the 8B `llama3-8b`; training quality and
   domain focus rival raw parameter count on a knowledge-intensive task. Size still matters at the
   low end (the 2B `gemma2-2b` finished last), so the scale–quality relation is real but
   non-monotonic.
7. **Judge bias generalizes across model pools.** Strictness differences and (bounded) self-preference
   appeared again in the small local pool, independently reproducing the Run A pattern — single-judge
   evaluation is unreliable in both settings.
8. **The ensemble is robust.** Run B's consensus ranking was stable across all four judges, the
   strongest single piece of evidence for the framework's central design claim.

## Cross-run observation
Both runs independently rank by an ensemble of diverse judges and both show the same qualitative
story: individual judges disagree on absolute scores, yet the *aggregated* ranking is coherent and
stable. (Absolute scores are **not** comparable across runs — each run has its own teachers,
questions, and rubric — so we compare *patterns*, not numbers.)

## Still to be completed after Run C
- Whether the bigger-isn't-always-better finding holds when same-vendor **size pairs**
  (gemma2 2b↔9b, qwen2.5 3b↔7b) compete directly.
- Whether the ensemble stays stable as the pool grows to ~7 models and ~20 questions.
- Final practical guidance: recommended pool size, role assignment, and question count for a stable
  ranking on a modest local setup.
