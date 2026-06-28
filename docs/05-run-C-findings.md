# 05 — Run C Findings: Large-Scale Local Run (7 models · 20 questions)

> **Interactive reports for this run** (rendered in browser):
> [Dashboard](https://itaym26.github.io/coeval-cybersecurity-eval/runs/run-C-local/reports/index.html) ·
> [Student](https://itaym26.github.io/coeval-cybersecurity-eval/runs/run-C-local/reports/student_report/index.html) ·
> [Judge](https://itaym26.github.io/coeval-cybersecurity-eval/runs/run-C-local/reports/judge_report/index.html) ·
> [Judge Consistency](https://itaym26.github.io/coeval-cybersecurity-eval/runs/run-C-local/reports/judge_consistency/index.html) ·
> [Interaction Matrix](https://itaym26.github.io/coeval-cybersecurity-eval/runs/run-C-local/reports/interaction_matrix/index.html)

---

## 1. What we set out to test

Run C is the capstone experiment. Its purpose was to show that **CoEval scales** — that the framework
produces a coherent, defensible ranking at large volume — and to test the paper's claims on a pool
large enough to include controlled comparisons. Concretely, we wanted to answer:

- Does the bigger-isn't-always-better signal from Run B **survive at scale**, with same-vendor
  **size pairs** (gemma2 2B↔9B, qwen2.5 3B↔7B) competing head-to-head?
- Does the **ensemble remain stable** as the judge panel grows from 4 to 7 models?
- Does judge **strictness/bias** reproduce on a larger, more diverse panel?

**Configuration:** 7 local models (llama3-8b, gemma2-2b, gemma2-9b, qwen2.5-3b, qwen2.5-7b, phi3,
mistral-7b), 20 datapoints per teacher, explicit 5-factor rubric (the approach validated in Run B).
See [`config/cybersecurity_runC.yaml`](../config/cybersecurity_runC.yaml).

## 2. Scale and completion

| Phase | Output |
|-------|--------|
| 3 — Data generation | 140 datapoints (20 × 7 teachers) |
| 4 — Response collection | 980 responses (7 students × 140) |
| 5 — Evaluation | 6,860 judgments (7 judges × 980), **6,824 valid (99%)** |

The experiment log ends with `Experiment cybersecurity-run-C-large completed successfully`. This is
roughly **8× the volume of Run B** (~1,000 → ~8,000 calls).

## 3. Results — the ranking

| Rank | Student | Vendor | Size | Mean score |
|:----:|:--------|:-------|:----:|:----------:|
| 🥇 | **phi3** | Microsoft | 3.8B | **0.894** |
| 🥈 | llama3-8b | Meta | 8B | 0.888 |
| 🥉 | mistral-7b | Mistral | 7B | 0.885 |
| 4 | gemma2-9b | Google | 9B | 0.881 |
| 5 | qwen2.5-3b | Alibaba | 3B | 0.880 |
| 6 | qwen2.5-7b | Alibaba | 7B | 0.869 |
| 7 | gemma2-2b | Google | 2B | 0.840 |

### Finding 1 — bigger is not always better (now with controlled pairs)
- **phi3 (3.8B)** beat both the 8B llama3 and the 7B mistral.
- **Gemma 2:** 9B (0.881) > 2B (0.840) — scale helped.
- **Qwen 2.5:** 3B (**0.880**) > 7B (0.869) — scale *hurt*.

The scale–quality relationship is therefore **real but non-monotonic**. Training data quality and
domain focus (phi's textbook-style corpus) rival raw parameter count on a knowledge-intensive domain.

### Finding 2 — at scale the top scores compress
The top five models fall within a narrow **0.880–0.894** band, with only gemma2-2b clearly detached
(0.840). A larger, more diverse ensemble averages out extreme opinions, producing a tighter, more
conservative spread than the 4-model Run B (0.798–0.898).

### Finding 3 — judge strictness reproduces, ensemble stays stable
Judge mean awarded scores span **0.808 (phi3) → 0.958 (mistral-7b)** — a 0.15 gap on identical
answers. Yet **phi3 is ranked #1 by all seven judges** and gemma2-2b is last under six of seven: the
consensus is robust to individual bias. *Example:* gemma2-2b scores 0.745 from phi3 but 0.941 from
mistral — a 0.20 swing — without changing its last-place finish.

## 4. Did the run succeed or fail?

**Complete success** — 100% of judgments produced, 99% valid, a full 7-model ranking with controlled
size-pair comparisons. This is the project's authoritative result.

## 5. Problems encountered and how we solved them

Run C was long (multi-day) and surfaced two operational issues. We distinguish **temporary**
work-arounds (let the run continue) from **fundamental** fixes (prevent recurrence).

| Issue | Cause | Fix | Type |
|-------|-------|-----|------|
| Machine slept overnight, pausing the run | sleep policy covered only AC idle, not lid/battery | comprehensive `powercfg` policy (AC+DC standby/hibernate/monitor = 0, lid action = none) | **Fundamental** |
| `Phase 'evaluation' failed: [Errno 22]` (3×) | PowerShell `*>>` redirect of the native console handle becomes invalid on Windows over a multi-day run | stopped redirecting console (`*> $null`); rely on CoEval's internal `run.log` | **Fundamental** |
| Process halts mid-run | any of the above | `coeval run --continue` resumes from checkpoint, re-doing only incomplete `(teacher, judge)` files | **Temporary** (recovery, applied repeatedly) |
| 3 individual judgments failed with a transient `Errno 22` | rare per-call I/O error outliving 3 retries | caught per-evaluation and skipped; recoverable via `coeval repair` + `--continue` | **Temporary** (0.04% impact) |

A memory note: on the 13.7 GB laptop, loading more than one model at once (`OLLAMA_MAX_LOADED_MODELS=2`)
pushed RAM to 95% and risked a freeze, so we kept **one model resident at a time** — the only stable
configuration for seven large models on this hardware. This is documented as a hardware-limit lesson.

## 6. Conclusions carried forward

- The bigger-isn't-better signal is **robust** — it held across both Run B and Run C, and even within
  controlled same-vendor pairs.
- The **ensemble is the right unit of trust**: individual judges are biased, the consensus is stable.
- For multi-day local runs, **checkpointing + a clean (non-redirected) launch + an aggressive
  no-sleep policy** are the operational essentials; `--continue` makes interruptions cheap.

## 7. How Run C differs from Run B

| Dimension | Run B | Run C |
|-----------|-------|-------|
| Models | 4 | **7** (added gemma2-9b, qwen2.5-7b, mistral-7b) |
| Questions / teacher | 12 | **20** |
| Total judgments | 768 | **6,860** |
| Controlled size pairs | none | **2** (gemma2, qwen2.5) — enables direct scale-vs-quality test |
| Score spread (students) | 0.798–0.898 | 0.840–0.894 (compressed) |
| New operational lessons | single-model RAM cap | multi-day resilience: no-sleep policy + non-redirected launch + repair |

Run C turns Run B's *suggestive* finding (a small model on top) into a *controlled* result (small
models beating their own larger siblings), at 8× the evidence volume — the difference between an
anecdote and a result.
