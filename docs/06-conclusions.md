# 06 — Conclusions: Our Results vs. the CoEval Paper

This document states our final conclusions and aligns them, **claim by claim**, with the measured
claims of the instructor's paper (see the paper summary in the project [README](../README.md) §6 and
the paper itself: <https://apartsinprojects.github.io/CoEval/>). Each verdict is **stated, then
justified with evidence from our runs and a concrete example.**

We tested the paper's five measured claims (C1–C5) by independently replicating CoEval on a **new
domain (cybersecurity)** and a **new, all-free model pool** the paper never used — a genuine
out-of-distribution stress test of its conclusions.

---

## C1 — Judge composition is a first-order variable — ✅ Confirmed

**Evidence.** In Run C the seven judges awarded mean scores spanning **0.808 (phi3) → 0.958
(mistral-7b)** on the *same* answers — a 0.15 gap attributable solely to judge identity. Run A showed
the same effect on the cloud pool (gpt-oss opened a 0.26 gap between the two students; llama3 only
0.02).

**Example.** Student `gemma2-2b` received **0.745** from judge `phi3` but **0.941** from judge
`mistral-7b`.

**Mapping to the paper.** This reproduces the paper's headline that agreement ranges from κ=0.003 to
κ=0.422 depending on *which* judges are paired — composition, not count, drives reliability.

---

## C2 — A multi-judge ensemble cancels single-judge bias — ✅ Confirmed

**Evidence.** Despite the strictness spread above, the aggregated ranking is stable. In Run C,
**phi3 is ranked #1 by all 7 judges**; gemma2-2b is last under 6 of 7. In Run B the consensus held
across all 4 judges.

**Example.** The most lenient judge (mistral, ~0.96 average) and the harshest (phi3, ~0.81 average)
disagree on absolute scores by ~0.15, yet **both** rank phi3 first and gemma2-2b last. The ordering
survives even though no single judge's numbers do.

**Mapping to the paper.** Directly supports the paper's central design rationale: aggregation
produces a bias-resistant ranking no individual judge would give alone.

---

## C3 — Small models are unreliable judges — ✅ Confirmed

**Evidence.** Structured-output reliability scaled with model size. In Run A only **51% of judgments
were valid JSON**, the bulk of the failures coming from the smallest free-tier judges. In early Run B
attempts the 2–3B models could not emit the complex JSON that *automatic* attribute/rubric generation
requires **at all**, forcing us to provide an explicit rubric. The smallest model, gemma2-2b, was
also the noisiest judge and weakest student.

**Example.** Phase-1 `target_attributes` generation failed JSON parsing for every small teacher until
we switched from `auto` to an explicit attribute/rubric specification.

**Mapping to the paper.** Matches the paper's finding that sub-2B models give near-random agreement
(κ≈0.003) and cannot be trusted as judges; we extend it with a second failure mode (malformed
structured output).

---

## C4 — Rankings are domain-specific; scale ≠ quality — ✅ Confirmed and extended

**Evidence.** On cybersecurity the 3.8B **phi3 outscored the 8B llama3 and 7B mistral**, and within a
single vendor family the smaller model sometimes won:

| Family | Small | Large | Winner |
|:-------|:-----:|:-----:|:------:|
| Gemma 2 | 2B → 0.840 | 9B → 0.881 | bigger |
| Qwen 2.5 | 3B → **0.880** | 7B → 0.869 | **smaller** |

**Example.** A generic "bigger/newer wins" leaderboard would have ranked qwen2.5-7b above
qwen2.5-3b; on *our* domain the 3B model scored higher.

**Mapping to the paper.** Reinforces the paper's domain-specificity claim and extends it: not only is
the *best* model domain-dependent, the *scale-to-quality* relationship is itself non-monotonic and
domain-dependent. Phi's textbook-style training appears especially suited to knowledge-dense security
content.

---

## C5 — Closed-loop LLM evaluation is cheap and fully automatable — ✅ Confirmed (stronger)

**Evidence.** We produced **6,860 judgments at $0.00** via local inference, with zero human labels
and zero manual steps between phases — versus the paper's $5.89 on paid APIs.

**Trade-off we document.** The cost moves from money to **time**: on a 13.7 GB laptop, Run C spanned
several days of checkpointed, resumable execution, constrained to one model in memory at a time.

**Mapping to the paper.** Confirms the cost-effectiveness claim and demonstrates an even cheaper
(fully local) operating point, at the price of wall-clock time.

---

## Limitations & Threats to Validity

A rigorous study must state where its conclusions are bounded. We group the threats by type.

### Construct validity (are we measuring the right thing?)
- **No human ground truth.** We did not collect expert human rankings for cybersecurity, so our
  ranking has **face validity** (sensible, internally consistent, stable across judges) rather than a
  *verified* correlation to human judgment. This is the same limitation the paper itself
  acknowledges. The unanimous failure of a factually-wrong RSA answer
  ([Example 2](08-qualitative-examples.md)) is supporting evidence that the rubric tracks correctness,
  but it is not a substitute for a human baseline.
- **Coarse score scale.** Judges emit only High/Medium/Low (mapped to 1.0/0.5/0.0). This is robust
  but low-resolution; small true differences between strong models may be quantization-limited
  (visible in the compressed 0.880–0.894 top band of Run C).

### Internal validity (could a confound explain the result?)
- **Self-participation.** Every model served as teacher, student, and judge, so self-preference is a
  confound. We *quantified* it ([§2 of the quantitative analysis](07-quantitative-analysis.md)):
  it is bounded, and critically the winner (phi3) is self-*critical*, so the headline result is not a
  self-inflation artifact — but the confound is mitigated, not eliminated.
- **Provisioning difference across runs.** Run A used `auto` attributes/rubric; Runs B and C used an
  explicit rubric (forced by small-model JSON limits). Absolute scores are therefore **not comparable
  across runs** — we compare *patterns* and *rank order*, never raw numbers between runs.

### External validity (how far does it generalize?)
- **One domain, one language.** All results are on English-language cybersecurity. Generalization to
  other domains/languages is unestablished (the paper shares this limit).
- **Small, free models only.** Our pool is 2B–9B open models; conclusions may not transfer to
  frontier-scale models. In particular, the "bigger isn't better" finding is demonstrated *within*
  this small-model regime.

### Statistical-conclusion validity
- **No confidence intervals on every metric.** We report point estimates for κ, ρ, and correlations;
  we did not bootstrap CIs for all of them. The headline rank-stability result (Spearman ρ = 1.000)
  rests on only four shared models, so it shows *perfect order preservation* on a small set rather
  than a tightly-estimated population parameter.
- **A few lost judgments.** 36 of 6,860 Run C judgments (0.5%) failed and were excluded; this is
  negligible but non-zero.

> These limitations are the natural scope boundaries of a free, single-laptop replication; none
> undercut the qualitative findings, and several (self-preference, rank stability) are *quantified*
> rather than merely assumed.

---

## Overall conclusion

Across three escalating experiments on a domain and model pool the paper never touched, **all five of
the paper's measured claims (C1–C5) reproduced.** The most striking result — that a 3.8B model tops a
field including 7–9B models, and that a 3B model beats its own 7B sibling — both confirms the paper's
domain-specificity claim and contributes a new, controlled illustration of it. The project also
yields a practical operations lesson the paper does not emphasize: for multi-thousand-call ensemble
evaluation on commodity hardware, **checkpointing, a clean non-redirected launch, an aggressive
no-sleep policy, and single-model memory loading** are what make the run actually finish.

### Practical guidance (our contribution)
- **Pool:** ≥4 cross-vendor models gives a stable ensemble; 7 tightens it further.
- **Judges:** avoid sub-2B models as judges; prefer a *diverse* panel over a *large* one.
- **Provisioning:** on small local models, supply an explicit rubric rather than relying on `auto`.
- **Operations:** local inference is free but time-bound — plan for multi-night, resumable runs.
