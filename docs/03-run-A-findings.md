# 03 — Run A Findings: Cloud Free-Tier (Partial)

## 1. Setup

Run A used a vendor-diverse pool of four free models — one local (Meta `llama3-8b` via Ollama) and
three OpenRouter `:free` models (OpenAI `gpt-oss-20b`, Google `gemma-4-31b`, NVIDIA
`nemotron-nano-9b`). Configuration: [`config/cybersecurity_cloud.yaml`](../config/cybersecurity_cloud.yaml).
Each model held all three roles; each Teacher generated 12 datapoints.

`coeval plan` estimated ~1,008 LLM calls, ~$0.29, ~91 minutes.

## 2. What completed

| Phase | Status | Output |
|-------|--------|--------|
| 1 — Attribute mapping | ✅ Complete | 30 target + 29 nuanced attributes |
| 2 — Rubric mapping | ✅ Complete | 19 scoring factors |
| 3 — Data generation | ✅ Complete | 48 datapoints (12 per teacher) |
| 4 — Response collection | ⚠️ Partial | 8 of 16 student×teacher sets (students `llama3-8b`, `gpt-oss-20b`) |
| 5 — Evaluation | ⚠️ Partial | 384 evaluation records, **194 valid** |

The two students whose answers completed (`llama3-8b`, `gpt-oss-20b`) were nonetheless scored by all
four judges across all four teachers — yielding a **complete two-model ranking**.

## 3. The rate-limit wall (a documented finding)

The run did not fail for any algorithmic reason. It hit OpenRouter's **account-wide free-tier
quota**:

```
Rate limit exceeded: free-models-per-min   (X-RateLimit-Limit: 16)
Rate limit exceeded: free-models-per-day    (X-RateLimit-Limit: 50)
```

- **16 requests/minute** and **50 requests/day**, shared across *all* `:free` models on the account.
- A full CoEval run needs ~1,000 calls — **20× the daily free allowance**.

We first improved the client's retry logic to honor the `Retry-After` header (see
[`02-methodology.md`](02-methodology.md) §6). This resolved the *per-minute* limit but the *per-day*
cap is an account-level wall no client-side change can bypass. **This is the central practical
lesson of Run A: free cloud LLM tiers are unsuitable for ensemble evaluation at scale.** It directly
motivated the fully-local Run B.

## 4. Validity rate as a model-quality signal

Of 384 evaluation attempts, only **194 (51%) produced parseable scores**. A large share of the
invalid records came from the smaller judges (`nemotron-nano-9b`, and `gemma-4-31b`) either emitting
malformed JSON or being truncated by rate-limit interruptions. The framework's robustness here is
worth noting: invalid judgments are *discarded* rather than silently coerced, so the ranking rests
only on well-formed scores. The ability to reliably emit structured, rubric-conformant JSON is
itself an informative dimension of judge quality.

## 5. Student ranking

Scores mapped High/Medium/Low → 1.0/0.5/0.0 and averaged across all judges and rubric factors
(reproducible via [`runs/run-A-cloud-free/compute_ranking.py`](../runs/run-A-cloud-free/compute_ranking.py)):

| Rank | Student model | Mean normalized score | n (valid judgments) |
|------|---------------|-----------------------|---------------------|
| 🥇 | **gpt-oss-20b** | **0.919** | 98 |
| 🥈 | **llama3-8b** | 0.775 | 96 |

The larger 20B-parameter OpenAI open model outscored the 8B Meta model on cybersecurity answers —
a result consistent with their relative scale.

## 6. Judge bias — the key methodological finding

Decomposing the same scores **by judge** reveals divergent behavior:

| Judge | Score for `gpt-oss-20b` | Score for `llama3-8b` | Gap |
|-------|------------------------|----------------------|-----|
| **gpt-oss-20b** (judging incl. itself) | 0.908 | 0.645 | **0.263** |
| **llama3-8b** (judging incl. itself) | 0.929 | 0.905 | 0.024 |

Two distinct biases appear:

1. **Divergent strictness.** `gpt-oss-20b` is a harsh judge that opens a 0.26 gap between the two
   students, while `llama3-8b` is lenient, separating them by only 0.02. The *same answers* receive
   very different score spreads depending on who judges.
2. **Self-preference signal.** Each judge rates the other-or-itself favorably in a way that, taken
   alone, would distort a ranking.

This is precisely the failure mode CoEval's **multi-judge ensemble** is designed to dampen: by
averaging across judges of differing strictness, the consensus ranking (`gpt-oss-20b` > `llama3-8b`)
is preserved while no single judge's idiosyncrasy dominates. Run A thus demonstrates *both* the
problem (individual-judge bias) and the framework's mitigation (ensemble aggregation) on real data.

## 7. Generated reports

Full interactive reports are in [`runs/run-A-cloud-free/reports/`](../runs/run-A-cloud-free/reports/)
(`coeval analyze all --partial-ok`): student report, judge report, judge-consistency, interaction
matrix, score distribution, coverage summary, and an Excel workbook. Screenshots are in
[`figures/`](../figures/).

## 8. Run A — Final Summary and Conclusions

### Did the run succeed or fail, and why?
Run A was a **partial success**. The framework's *methodology* worked end-to-end on real data —
attributes, rubric, questions, answers, and judgments were all produced, and a valid two-model
ranking was recovered. However, the run **did not complete** for all four models. The cause was
**not algorithmic** but **infrastructural**: OpenRouter's free tier enforces an account-wide cap of
**50 requests/day and 16/minute**, shared across every `:free` model. A full CoEval run needs
~1,000 calls — roughly 20× the daily allowance — so the cloud students `gemma-4-31b` and
`nemotron-nano-9b` were rate-limited out before completing as students. A secondary factor was
**structured-output unreliability**: only 51% of judgments parsed as valid JSON, with the smaller
models contributing most failures.

### What conclusions did we draw?
1. **CoEval's automatic provisioning is effective** — from one paragraph it produced a domain-faithful
   attribute space and an expert-aligned 19-factor rubric.
2. **Individual judges are biased** (strictness gap of 0.26 vs 0.02 on identical answers; visible
   self-preference) — empirically motivating the **multi-judge ensemble** that the framework provides.
3. **The consensus ranking was still recovered** (`gpt-oss-20b` 0.919 > `llama3-8b` 0.775),
   demonstrating the ensemble's value even on partial data.
4. **Free cloud tiers are unsuitable for ensemble evaluation at scale** — the daily cap is a hard wall.

### How will we act on this going forward?
- **Switch to fully-local inference (Ollama) for Run B** to eliminate rate limits and guarantee a
  complete, reproducible run.
- **Provide an explicit, compact rubric and attributes in Run B** instead of `auto`, because small
  local models cannot reliably emit the large JSON structures that auto-mode requires. Reusing a
  rubric distilled from Run A also makes the two runs directly comparable.
- **Carry the judge-bias and validity-rate analyses into Run B** to test whether the same patterns
  hold for a pool of small local models.
