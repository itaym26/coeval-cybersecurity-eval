# 06 — Summary of the CoEval Paper

> *CoEval: Ranking Language Models for Custom Tasks Without Labeled Data or Trustworthy Benchmarks*
> **Alexander Apartsin** (Holon Institute of Technology) · **Yehudit Aperstein** (Afeka Tel Aviv Academic College of Engineering)
> Online (HTML, rendered math): <https://apartsinprojects.github.io/CoEval/>

This is a faithful, condensed summary of the instructor's paper, written so that our own
experimental conclusions can later be measured against it (see [`05-conclusions.md`](05-conclusions.md)).

---

## 1. What problem does the paper attack?

Practitioners who must pick an LLM for a *specific* deployment face a trilemma:

- **Human-curated benchmarks** are expensive ($0.10–$1.00 per annotation) and locked to one domain.
- **LLM-as-judge** shortcuts are cheap but biased — positional preference reverses **20–27%** of
  pairwise rankings, and a single judge's correlation with human ratings drops **below ρ ≈ 0.40** on
  open-ended generation.
- **Naive synthetic generation** lacks stratified sampling, so it omits rare but deployment-critical
  conditions.

No prior framework unifies *controlled generation + structured rubrics + multi-judge ensemble scoring
+ calibration* into one automated pipeline. That is the gap CoEval fills.

## 2. The proposed method

A **Teacher / Student / Judge** paradigm for a self-evaluating LLM ensemble:

- **Teachers** define the evaluation space — enumerate quality attributes, author rubric criteria,
  and generate reference (prompt, response) pairs via **attribute-stratified sampling** that
  guarantees coverage of the whole quality space (including low-frequency cases).
- **Students** produce candidate responses (the models being evaluated).
- **Judges** independently score each response against the rubric; **OLS calibration** corrects for
  verbosity and positional bias so the ensemble can be aggregated **without any human annotation**.

The framework also defines **label-free selection signals** — teacher discrimination (V1/S2/R3) and
judge consensus (J*) — and a **doubly-robust ranking** that down-weights unreliable contributors.

## 3. The hypotheses being tested

1. **Attribute-stratified generation** produces more representative evaluation corpora than
   uncontrolled generation.
2. **Multi-judge ensembles with calibration reduce bias** relative to a single judge.
3. **Closed-loop LLM evaluation is cost-effective at scale** (target: ~8,000 evaluations for a few
   dollars, orders of magnitude cheaper than human annotation).

## 4. Experimental validation

Validated on **`medium-benchmark-v1`**: four NLP tasks (text summarization, code explanation, email
composition, data interpretation) × five models (GPT-4o-mini, GPT-3.5-Turbo, Qwen2.5-0.5B/1.5B,
SmolLM2-1.7B). The pipeline produced **7,978 evaluations for $5.89 in 12.8 hours**, fully automated.

Key measured results:

| Finding | Evidence |
|:--------|:---------|
| Judge composition is a **first-order** reliability variable | pairwise agreement κ = **0.003** (SmolLM2-1.7B, near-random) → **0.422** (GPT-3.5 × GPT-4o-mini, ≈ human-level) |
| **Small (<2B) models fail as judges** | SmolLM2-1.7B κ ≈ 0.003–0.033 |
| **Student ordering has face validity** | GPT-4o-mini 0.807 > GPT-3.5 0.768 > Qwen2.5-1.5B 0.641 > SmolLM2-1.7B 0.598 > Qwen2.5-0.5B 0.521 |
| **Rubric concreteness matters** | *technical_accuracy* SPA = 0.843 vs *professionalism* SPA = 0.294 |
| **Cost-effective** | $0.00074 per judgment; Phase 5 dominates (76% of cost) |
| **Teacher discrimination paradox** | the *smallest* model (SmolLM2-1.7B, V1 = 0.0046) was the most discriminating teacher |

## 5. Which hypotheses were proven?

- ✅ **Confirmed:** judge capability correlates with inter-rater agreement; concrete rubric criteria
  give higher consistency; the pipeline is cheap and fully automated.
- ❓ **Complicated / not cleanly confirmed:** "stronger models make better teachers" — the most
  discriminating teacher was a *small* model, implying prompt diversity (not generation quality)
  drives discrimination. The authors flag this as needing further statistical validation.
- ⚠️ **Stated as projection, not measured:** the headline superiority of CoEval over G-Eval /
  BERTScore / ROUGE (Table 9) and parts of the ablation are explicitly **simulated**, pending a
  ground-truth study.

## 6. Limitations the authors acknowledge

1. **Self-evaluation contamination** — GPT models acted as teacher, student, and judge
   simultaneously, an unresolved confound on ~6–18% of evaluations.
2. **Simulated comparisons** against baselines were not empirically measured.
3. **Small open-weight judges fail**, pushing reliable use toward paid commercial APIs.
4. **Limited scope** — four English tasks, five models; generalization unproven.
5. **No human baseline** was collected.

## 7. The marketing README vs. the paper — a note

The repository's README advertises stronger, rounded numbers (e.g. ρ = 0.86 / 0.95 rank recovery,
93% verbosity-bias reduction, "0.0000 13-gram overlap", $5.89 for 7,978 evals). The **paper itself**
is more conservative: several of those comparative figures are **projections flagged for future
measurement**, and the firmly *measured* contributions are the judge-agreement range, the
student-ordering face validity, the rubric-concreteness effect, and the cost. We treat the **paper's
measured claims** as the reference point when aligning our own results.
