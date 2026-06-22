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

## To be completed after Run B
- A full four-model ranking and whether it agrees with Run A's two-model ordering.
- Whether local small models reproduce the judge-bias pattern seen in the cloud pool.
- Practical guidance: minimum pool size, role assignment, and datapoint count for a stable ranking
  on a modest local setup.
