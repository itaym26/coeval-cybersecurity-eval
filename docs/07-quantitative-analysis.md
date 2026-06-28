# 07 — Quantitative Analysis

This document reports the statistical measures we computed on **Run C** (7 models, 980 responses,
6,824 valid judgments) to put the project's claims on a numerical footing and to compare them
*directly* to the metrics used in the instructor's paper (Cohen's κ, Spearman ρ, verbosity
correlation). All measures are computed by a dependency-free script,
[`runs/run-C-local/analyze_stats.py`](../runs/run-C-local/analyze_stats.py), so they are fully
reproducible.

---

## 1. Inter-judge agreement (Cohen's κ)

For every pair of judges we collected all (response, rubric-factor) cells they both scored, mapped
the High/Medium/Low labels to categories, and computed Cohen's κ.

| Statistic | Value |
|-----------|-------|
| κ range | **+0.131 … +0.309** |
| Mean κ | **+0.198** |
| Highest-agreeing pair | gemma2-9b × qwen2.5-7b (0.309) |
| Lowest-agreeing pair | gemma2-2b × phi3 (0.131) |

**Interpretation.** All pairs fall in the "slight-to-fair" agreement band (κ ≈ 0.13–0.31), and
**every pair is positive** — there are no near-random judges. This is consistent with the paper's
finding that agreement depends heavily on *which* models judge (the paper reports κ from 0.003 to
0.422). Notably, our **lowest**-agreeing pairs all involve the **smallest** model, `gemma2-2b` (2B) —
echoing the paper's result that small models are the weakest judges, while our pool avoids the
near-zero κ the paper saw only for a sub-2B model. **→ supports claims C1 and C3.**

## 2. Self-preference index

For each model we compared the score it gives *itself* as a judge to the mean score the *other*
judges give it (both as a student). A positive value means the model inflates its own work.

| Model | self | others | bias |
|-------|:----:|:------:|:----:|
| mistral-7b | 0.963 | 0.872 | **+0.091** |
| llama3-8b | 0.945 | 0.879 | **+0.066** |
| gemma2-2b | 0.866 | 0.836 | +0.030 |
| gemma2-9b | 0.902 | 0.878 | +0.024 |
| qwen2.5-7b | 0.863 | 0.870 | −0.008 |
| qwen2.5-3b | 0.879 | 0.880 | −0.001 |
| phi3 | 0.858 | 0.900 | **−0.042** |

**Interpretation.** Self-preference is **real but bounded and inconsistent**: two models (mistral,
llama3) clearly over-rate themselves, three are neutral, and — most importantly — the overall
**winner, `phi3`, is self-*critical* (−0.042)**. phi3's first-place finish therefore **cannot** be an
artifact of self-inflation; if anything it is *understated* by its own harsh self-scoring. This both
confirms that single-judge scoring is biased and strengthens the validity of the ensemble ranking.
**→ supports C1; reinforces the need for C2 (ensemble).**

## 3. Verbosity bias — where our results *diverge* from the paper

The paper claims a multi-judge ensemble cancels the verbosity bias (preference for longer answers)
that no single judge avoids, reducing the length–score correlation to r ≈ +0.010 (a 93% reduction).
We tested the same on our data: correlation between answer length (characters) and score.

| Estimator | Length–score correlation |
|-----------|:------------------------:|
| **Ensemble** (mean of 7 judges) | Pearson r = **+0.120** |
| Mean of single-judge \|r\| | **0.112** |
| Per-judge range | −0.089 (gemma2-9b) … +0.181 (gemma2-2b) |

**Interpretation — a partial non-replication.** In our pool the verbosity bias is **weak overall
(r ≈ 0.12)** but the ensemble does **not** cancel it — the ensemble correlation (0.120) is essentially
the same as the average single-judge magnitude (0.112), not lower. The reason is visible in the
per-judge numbers: six of seven judges share a *mildly positive* length preference, so averaging them
**reinforces** rather than offsets the bias. Cancellation requires judges whose biases point in
*different directions*; the paper's pool happened to have that property, ours largely does not. This
is an honest, interesting divergence: **ensemble aggregation cancels bias only when the panel's
individual biases are diverse enough to offset — it is not automatic.** **→ qualifies the paper's
verbosity claim.**

## 4. Rank stability across runs (Spearman ρ)

Four models appear in both Run B (4 models) and Run C (7 models). We correlated their Run B ranking
with their Run C ranking.

| Model | Run B | Run C |
|-------|:-----:|:-----:|
| phi3 | 0.898 | 0.894 |
| llama3-8b | 0.860 | 0.888 |
| qwen2.5-3b | 0.856 | 0.880 |
| gemma2-2b | 0.798 | 0.840 |

**Spearman ρ (B vs C) = +1.000** — a *perfect* rank correlation.

**Interpretation.** Despite Run C adding three new competitors, tripling the questions, and growing
the judge panel from 4 to 7, the four shared models keep **exactly** the same order. This is strong
evidence that CoEval's ranking is **stable and reproducible** for this domain, not an artifact of a
particular run's configuration. **→ supports C2 and the reproducibility premise of the framework.**

---

## Summary

| Measure | Result | Bearing on the paper |
|---------|--------|----------------------|
| Inter-judge κ | +0.131 … +0.309 (mean +0.198) | ✅ supports C1/C3 |
| Self-preference | bounded; winner is self-critical | ✅ supports C1; validates ranking |
| Verbosity bias | ensemble r=+0.120 ≈ single-judge | ⚠️ **qualifies** the paper's cancellation claim |
| Rank stability (B↔C) | Spearman ρ = +1.000 | ✅ supports reproducibility / C2 |

Three of four measures reproduce the paper on a new domain; the verbosity result is a principled,
evidence-backed qualification — exactly the kind of nuance an independent replication is meant to
surface.
