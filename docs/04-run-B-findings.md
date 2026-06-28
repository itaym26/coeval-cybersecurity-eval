# 04 — Run B Findings: Fully Local (Complete)

> **Interactive reports for this run** (rendered in browser):
> [Dashboard](https://itaym26.github.io/coeval-cybersecurity-eval/runs/run-B-local/reports/index.html) ·
> [Student](https://itaym26.github.io/coeval-cybersecurity-eval/runs/run-B-local/reports/student_report/index.html) ·
> [Judge](https://itaym26.github.io/coeval-cybersecurity-eval/runs/run-B-local/reports/judge_report/index.html)

## 1. Setup

Run B used a **fully local** pool of four models served through Ollama, eliminating every cloud
rate-limit. Configuration: [`config/cybersecurity_runB.yaml`](../config/cybersecurity_runB.yaml).

| Model | Vendor | Size |
|-------|--------|------|
| `llama3-8b` | Meta | 8B |
| `gemma2-2b` | Google | 2B |
| `qwen2.5-3b` | Alibaba | 3B |
| `phi3` | Microsoft | 3.8B |

Each model held all three roles; each teacher generated 12 datapoints. Because small local models
could not reliably emit the JSON required by `auto` attribute/rubric generation, we supplied
**explicit** attributes and a **compact 5-factor rubric** distilled from Run A's auto-generated 19
(see [`02-methodology.md`](02-methodology.md) §2). Judges scored on the High/Medium/Low scale,
mapped to 1.0/0.5/0.0.

## 2. Completion

| Phase | Status |
|-------|--------|
| 1 — Attribute mapping | ✅ Complete (static) |
| 2 — Rubric mapping | ✅ Complete (static) |
| 3 — Data generation | ✅ Complete — 48 datapoints (12 × 4 teachers) |
| 4 — Response collection | ✅ Complete — all 16 student×teacher sets |
| 5 — Evaluation | ✅ Complete — 768 attempts, **764 valid (99%)** |

The experiment log ends with `Experiment cybersecurity-run-B-local completed successfully`. Total
wall-clock time ≈ 3.5 hours on a 13.7 GB laptop with `OLLAMA_MAX_LOADED_MODELS=1` (one model in
memory at a time). Only 4 of 768 judgments failed (isolated `phi3` JSON errors and two timeouts) —
a **99% validity rate**, versus 51% in the rate-limited Run A. *Removing the rate-limit wall not
only completed the run but dramatically improved data quality.*

## 3. Student ranking

Mean normalized score across all judges and rubric factors
([`runs/run-B-local/compute_ranking.py`](../runs/run-B-local/compute_ranking.py)):

| Rank | Student | Vendor | Size | Mean score | n |
|------|---------|--------|------|-----------|---|
| 🥇 | **phi3** | Microsoft | 3.8B | **0.898** | 191 |
| 🥈 | **llama3-8b** | Meta | 8B | 0.860 | 192 |
| 🥉 | **qwen2.5-3b** | Alibaba | 3B | 0.856 | 191 |
| 4 | **gemma2-2b** | Google | 2B | 0.798 | 190 |

## 4. Finding 1 — bigger is *not* always better

The headline result contradicts a naive "larger model wins" assumption: **`phi3` (3.8B) outscored
`llama3-8b` (8B)** on cybersecurity answers, despite having less than half the parameters. Microsoft's
Phi family is explicitly trained on dense, textbook-quality technical data, which appears to pay off
on a knowledge-intensive domain like cybersecurity. At the same time, the **smallest** model
(`gemma2-2b`, 2B) finished last — so size still matters at the low end. The relationship between
scale and quality is real but **non-monotonic**, and is exactly the kind of nuance a same-vendor
size-pair comparison (planned for Run C) can probe further.

## 5. Finding 2 — judge strictness varies widely

Decomposing scores by judge shows large differences in how harshly each model grades:

| Judge | Mean score it awarded | Behavior |
|-------|----------------------|----------|
| `llama3-8b` | ~0.888 | Lenient |
| `gemma2-2b` | ~0.877 | Lenient |
| `qwen2.5-3b` | ~0.800 | Moderate |
| `phi3` | ~0.807 | **Strict** |

`phi3` is both the best student *and* the harshest judge — it awarded its top student only 0.843,
whereas `llama3-8b` awarded its top student 0.942. The *same answers* receive systematically
different scores depending on who grades, confirming on a second, independent model pool the
judge-bias pattern first seen in Run A.

## 6. Finding 3 — self-preference is present but bounded

Looking at how each judge scores *itself*:

- `phi3` ranks itself **1st** (0.843) — self-preferring, but it is the consensus #1 anyway.
- `qwen2.5-3b` ranks itself **2nd** (0.823), above its overall 3rd-place finish — mild self-lift.
- `llama3-8b` ranks itself **2nd** (0.940), just behind phi3 — mild self-lift.
- `gemma2-2b` ranks itself **last** (0.849) — notably *self-critical*, no self-preference.

Self-preference exists but is modest and inconsistent, and **no single judge's bias overturns the
consensus**.

## 7. Finding 4 — the ensemble ranking is robust

Despite the strictness and self-preference differences above, the ordering is remarkably stable:

- **`phi3` is ranked #1 by all four judges.**
- `llama3-8b` is ranked #2 by three of four judges.
- `gemma2-2b` is ranked last by three of four judges.

This is the central argument *for* CoEval's design: aggregating a diverse judge panel cancels
individual idiosyncrasies and yields a ranking no single (biased) judge would give alone. The
framework recovered a coherent, defensible ordering from noisy individual opinions.

## 8. Generated reports

Full interactive reports: [`runs/run-B-local/reports/`](../runs/run-B-local/reports/) — student
report, judge report, judge-consistency, teacher differentiation, interaction matrix, score
distribution, coverage, and an Excel workbook. Screenshots in [`figures/`](../figures/).

---

## 9. Run B — Final Summary and Conclusions

### Did the run succeed or fail, and why?
**Complete success.** All five phases finished, producing a full four-model ranking from 764 valid
judgments (99%). The success is directly attributable to two corrective decisions made after Run A
and the first Run B attempt: (1) **going fully local** removed the OpenRouter daily-quota wall, and
(2) **supplying an explicit rubric/attributes** sidestepped the small models' inability to generate
complex JSON. Capping Ollama to one loaded model at a time resolved the only remaining obstacle — a
memory freeze on the 13.7 GB machine.

### What conclusions did we draw?
1. **CoEval produces a clean, complete ranking on commodity hardware** — no API budget, no cloud,
   fully reproducible.
2. **Model scale is not destiny:** `phi3` (3.8B) beat `llama3-8b` (8B); data quality and training
   focus matter as much as parameter count on a knowledge domain.
3. **Judge bias generalizes:** strictness and self-preference appeared again in a completely
   different (small, local) model pool — reinforcing that single-judge evaluation is unreliable.
4. **The ensemble works:** the consensus ranking was stable across all four judges, validating the
   framework's core premise.
5. **Removing rate limits improves data quality**, not just completeness (99% vs 51% valid).

### How will we act on this going forward?
- **Proceed to Run C — the final large-scale run.** Expand the pool to ~7 local models, explicitly
  including same-vendor **size pairs** (`gemma2` 2b↔9b, `qwen2.5` 3b↔7b) to test the
  bigger-isn't-always-better finding directly, and increase the question count to ~20 for a richer,
  more statistically grounded benchmark.
- **Reuse the explicit-rubric approach** that made Run B reliable.
- **Carry all four analyses** (ranking, size-vs-performance, judge bias, ensemble robustness) into
  Run C at larger scale, completing the project's arc from small exploratory runs to one
  authoritative result.

## 10. How Run B differs from Run A

| Dimension | Run A (cloud) | Run B (local) |
|-----------|---------------|---------------|
| Provider | OpenRouter free-tier + 1 local | Fully local (Ollama) |
| Outcome | Partial (rate-limited) | **Complete** |
| Usable students | 2 | **4** |
| Valid judgments | 194 / 384 (**51%**) | 764 / 768 (**99%**) |
| Provisioning | `auto` attributes + rubric | **explicit** rubric (small models can't emit the JSON) |
| Blocking issue | account-wide 50-requests/day cap | RAM freeze — solved by single-model loading |
| Role of the run | exposed the *problem* (free cloud doesn't scale) | delivered the first *clean result* |

In short, Run A proved that a free **cloud** ensemble run is infeasible and surfaced judge bias on a
2-model ranking; Run B removed the infrastructure ceiling by going **local**, lifting data validity
from 51% to 99% and producing the project's first complete, reproducible 4-model ranking — the
foundation that Run C then scales up.
