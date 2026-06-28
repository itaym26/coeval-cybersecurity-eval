<p align="center">
  <img src="figures/banner.svg" alt="CoEval × Cybersecurity — Teacher · Student · Judge evaluation ensemble" width="900"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/domain-cybersecurity-0ea5e9"/>
  <img src="https://img.shields.io/badge/framework-CoEval-success"/>
  <img src="https://img.shields.io/badge/runs-3%20(A·B·C)-informational"/>
  <img src="https://img.shields.io/badge/models-7%20local-blue"/>
  <img src="https://img.shields.io/badge/judgments-6%2C860-brightgreen"/>
  <img src="https://img.shields.io/badge/cost-%240.00%20(local)-yellow"/>
  <img src="https://img.shields.io/badge/python-%E2%89%A53.10-blue?logo=python&logoColor=white"/>
</p>

<p align="center">
  <b>A capstone study applying <a href="https://github.com/ApartsinProjects/CoEval">CoEval</a> — an ensemble-based, label-free LLM evaluation framework — to rank freely available language models on <b>cybersecurity</b> knowledge and reasoning.</b>
</p>

---

## 📄 Abstract

Choosing the best Large Language Model for a specialized domain is hard: public leaderboards may be **contaminated** by pretraining leakage, and building a labeled benchmark is a project in itself. **CoEval** (created by the course instructor, Dr. Alexander Apartsin) sidesteps both problems by letting a pool of models evaluate *each other* through three rotating roles — **Teacher** (writes fresh questions), **Student** (answers), and **Judge** (scores against an auto-generated rubric).

This project applies CoEval end-to-end to the domain of **cybersecurity**, using only **free** models (local models via [Ollama](https://ollama.com) and free-tier APIs via [OpenRouter](https://openrouter.ai)). We designed and executed **three escalating experiments** — from a partial cloud run, through a clean 4-model local run, to a large **7-model, 140-question, 6,860-judgment** run — and analyzed the resulting rankings, judge agreement, and bias signals. A recurring, paper-aligned finding emerged: **model scale is not destiny, and single-judge bias is real but is cancelled by the ensemble.**

---

## 🎯 The Challenge — why a custom cybersecurity benchmark?

|     | Challenge | Why it hurts here |
|:---:|:----------|:------------------|
| 🎯 | **Generic benchmarks don't transfer** | A model's MMLU score says little about whether it explains a SQL-injection mitigation correctly. |
| 🕳️ | **Leakage inflates scores** | Public security quizzes (OWASP, CVE write-ups) are all over the web and likely in pretraining. |
| 🧩 | **Hand-building a security benchmark is hard** | Writing balanced questions across network, web, crypto, and malware — with a rubric — is expensive. |
| 💸 | **Running many models × many questions is costly** | A full multi-model sweep multiplies tokens fast. |

> **Our answer:** let CoEval *generate* a fresh, contamination-free cybersecurity benchmark and let a **cross-model judge ensemble** rank the candidates — at **zero cost**, fully locally.

---

## 💡 The Concept — models evaluate each other

```
┌──────────────────────────────────────────────────────────────┐
│                   MODEL  ENSEMBLE  (7 models)                  │
│                                                                │
│   llama3 · gemma2-2b · gemma2-9b · qwen2.5-3b · qwen2.5-7b     │
│   phi3 · mistral-7b        — every model plays every role —    │
│                                                                │
│        ┏━━━━━━━━━━━━━ ROTATING ROLE ASSIGNMENT ━━━━━━━━━━━┓     │
│        ▼                       ▼                        ▼      │
│   🎓 TEACHER              📝 STUDENT               ⚖️ JUDGE     │
│  generates fresh        answers every            scores every  │
│  cybersecurity Qs       teacher's questions      answer 0–1    │
│  + reference answers    (the models tested)      vs. rubric    │
└──────────────────────────────────────────────────────────────┘
```

CoEval runs a **five-phase pipeline**, each phase checkpointed and resumable:

```
YAML Config →  Phase 1  Attribute Mapping   (dimensions of the domain)
            →  Phase 2  Rubric Mapping       (scoring criteria)
            →  Phase 3  Data Generation      (teachers write questions)
            →  Phase 4  Response Collection  (students answer)
            →  Phase 5  Evaluation           (judges score)  →  reports
```

---

## 🔬 Project design — three escalating experiments

We deliberately structured the work as an **evolution**, each run answering a question raised by the previous one:

| Run | Tier | Models | Questions | Result | What it taught us |
|:---:|:-----|:------:|:---------:|:-------|:------------------|
| **A** | Cloud free-tier + 1 local | 4 (2 usable) | 12 | ⚠️ Partial | Free cloud APIs are capped at **50 requests/day** — unusable at scale |
| **B** | Fully local (Ollama) | 4 | 12 | ✅ Complete | A clean, reproducible ranking; **a 3.8B model beat an 8B one** |
| **C** | Fully local — **large** | **7** | **20** | ✅ Complete | The capstone: **6,860 judgments**, size-vs-performance pairs, stable ensemble |

> The full chronological story of **every** run (including four early failed configurations and how each was diagnosed and fixed) is in **[docs/00-run-log.md](docs/00-run-log.md)**.

---

## 🏆 Headline Results

### Run C — final ranking (7 models, 140 questions, 6,824 valid judgments)

<p align="center"><img src="figures/runC_ranking.svg" alt="Run C ranking bar chart" width="820"/></p>

| Rank | Model | Vendor | Size | Score |
|:----:|:------|:-------|:----:|:-----:|
| 🥇 | **phi3** | Microsoft | 3.8B | **0.894** |
| 🥈 | llama3 | Meta | 8B | 0.888 |
| 🥉 | mistral | Mistral | 7B | 0.885 |
| 4 | gemma2 | Google | 9B | 0.881 |
| 5 | qwen2.5 | Alibaba | 3B | 0.880 |
| 6 | qwen2.5 | Alibaba | 7B | 0.869 |
| 7 | gemma2 | Google | 2B | 0.840 |

### Three standout findings

**1️⃣ Bigger is not always better.** The 3.8B **phi3** topped the ranking in *both* the 4-model and 7-model runs, beating models twice its size. And within a single family the bigger model did **not** always win:

| Family | Small | Large | Winner |
|:-------|:-----:|:-----:|:------:|
| Gemma 2 | 2B → 0.840 | 9B → 0.881 | ⬆️ bigger |
| Qwen 2.5 | 3B → **0.880** | 7B → 0.869 | ⬇️ **smaller!** |

**2️⃣ Judges are biased — strictness varies enormously.** The *same answers* get very different scores depending on who grades them:

<p align="center"><img src="figures/judge_strictness.svg" alt="Judge strictness bar chart" width="820"/></p>

**3️⃣ The ensemble cancels the bias.** Despite that spread, the consensus ranking is **stable**: phi3 is #1 across the board and gemma2-2b is consistently last. Aggregating a diverse judge panel recovers a coherent ordering that no single (biased) judge would give — the core promise of CoEval, reproduced on our data.

---

## 💻 What a run actually looks like

**1 — Probe every model (no cost):**

```text
$ coeval probe --config config/cybersecurity_runC.yaml
Probe: testing 7 model(s) (mode='full', on_fail='abort') ...
  gemma2-2b   [OK]   gemma2-9b  [OK]   llama3-8b   [OK]   mistral-7b [OK]
  phi3        [OK]   qwen2.5-3b [OK]   qwen2.5-7b  [OK]
Total: 7 available, 0 unavailable
```

**2 — Run the five-phase pipeline:**

```text
$ coeval run --config config/cybersecurity_runC.yaml
Phase 'attribute_mapping' completed
Phase 'rubric_mapping'   completed
Phase 3: (teacher='phi3') — generating 20 datapoints
Phase 4: (teacher='llama3-8b', student='mistral-7b') — collecting 20 responses
Phase 5: (teacher='qwen2.5-7b', judge='phi3') — evaluating 140 responses with 5 factor(s)
...
Experiment cybersecurity-run-C-large completed successfully
```

**3 — A judge's scored output (one Phase-5 record):**

```json
{
  "response_id": "cybersecurity__llama3-8b__00001__gpt-oss-20b",
  "judge_model_id": "gpt-oss-20b",
  "scores": {
    "Technical Accuracy": "High",
    "Theoretical Understanding": "High",
    "Practical Insight": "High",
    "Completeness": "Medium",
    "Clarity": "High"
  }
}
```

**4 — Generate interactive reports:**

```bash
coeval analyze all --run ./Runs/cybersecurity-run-C-large --out ./reports
```

📊 **Interactive HTML reports** (student / judge / teacher / consistency / interaction / score-distribution) and an Excel workbook are included for every run under [`runs/`](runs/).

---

## 📚 The CoEval Paper — what the instructor set out to prove

> *CoEval: Ranking Language Models for Custom Tasks Without Labeled Data or Trustworthy Benchmarks* —
> Alexander Apartsin (Holon Institute of Technology) & Yehudit Aperstein (Afeka College).
> [Read online](https://apartsinprojects.github.io/CoEval/).

**The problem.** Static benchmarks are expensive, non-extensible, and don't reflect a specific deployment's data or quality criteria; meanwhile "LLM-as-judge" shortcuts introduce systematic biases (positional preference flips 20–27% of pairwise rankings; single-judge correlation with humans falls below ρ≈0.40 on open-ended tasks). No prior method builds **task-specific, attribute-controlled benchmarks with calibrated multi-judge scoring** and zero human labels.

**The three hypotheses the paper tests:**
1. **Attribute-stratified generation** yields more representative benchmarks — covering rare, deployment-critical conditions that uncontrolled generation omits.
2. **Multi-judge ensembles + calibration reduce bias** versus a single judge.
3. **Closed-loop LLM evaluation is cost-effective at scale** (7,978 evaluations for **$5.89**, 135–1,354× cheaper than human annotation).

**What the paper found (validated on `medium-benchmark-v1`: 4 tasks, 5 models):**
- ✅ **Judge composition is a first-order variable.** Pairwise agreement ranged from κ=0.003 (a sub-2B model, near-random) to κ=0.422 (GPT-3.5×GPT-4o-mini, ≈ human-level). **Small models cannot be trusted as judges.**
- ✅ **Cost-effectiveness confirmed:** $0.00074 per judgment, fully automated.
- ✅ **Student ordering had face validity** (GPT-4o-mini > GPT-3.5 > Qwen2.5-1.5B > SmolLM2 > Qwen2.5-0.5B), matching community priors.
- ⚠️ **Concrete rubric criteria** (e.g. *technical_accuracy*, SPA=0.843) far outperform abstract ones (*professionalism*, SPA=0.294).
- ❓ **Complicated:** the assumption that *stronger models make better teachers* did **not** cleanly hold — a small model (SmolLM2-1.7B) was the most *discriminating* teacher, suggesting prompt diversity, not raw quality, drives discrimination.

**Honest limitations the authors flag:** some headline comparisons (vs. G-Eval, BERTScore) are **projections, not measured**; GPT models served as teacher+student+judge simultaneously (self-evaluation contamination); no human baseline; only English, 4 tasks, 5 models.

📖 A fuller standalone summary lives in **[docs/06-paper-summary.md](docs/06-paper-summary.md)**.

---

## 🔗 How our experiments relate to the paper *(preliminary)*

Our runs are an **independent replication on a new domain (cybersecurity) and a new, all-free model pool** — a useful stress test of the paper's claims. Early alignment:

| Paper claim | Our evidence | Verdict |
|:------------|:-------------|:-------:|
| Judge composition / strictness is first-order | Judge means ranged 0.81 (phi3) → 0.96 (mistral) on identical answers | ✅ **Supports** |
| Ensemble aggregation cancels single-judge bias | Consensus ranking stable across all 7 judges despite the spread | ✅ **Supports** |
| Small models are weak judges | Smallest model (gemma2-2b) was the harshest/most erratic and produced most invalid JSON | ✅ **Supports** |
| Bigger model ≠ better | phi3 (3.8B) beat 8B/7B; qwen2.5-3B beat qwen2.5-7B | ✅ **Supports / extends** |
| Stronger model = better teacher (paper: complicated) | *to analyze from our teacher-discrimination data* | ⏳ pending |

> A complete, rigorous alignment (claim-by-claim, with our statistics) is the next deliverable — see [docs/05-conclusions.md](docs/05-conclusions.md).

---

## 🗂️ Repository structure

```
coeval-cybersecurity-eval/
├── README.md                       ← this file
├── config/                         the three experiment configs (A / B / C)
├── runs/
│   ├── run-A-cloud-free/           artifacts + reports + ranking script
│   ├── run-B-local/
│   └── run-C-local/                the large final run
├── docs/
│   ├── 00-run-log.md               chronological log of every run (success/failure + cause)
│   ├── 01-domain-background.md      cybersecurity concepts primer
│   ├── 02-methodology.md           CoEval mechanics + our configuration
│   ├── 03-run-A-findings.md        Run A analysis + conclusions
│   ├── 04-run-B-findings.md        Run B analysis + conclusions
│   ├── 05-conclusions.md           comparative conclusions (+ paper alignment)
│   └── 06-paper-summary.md         standalone summary of the instructor's paper
├── scripts/                        RAM-safe overnight run scripts
└── figures/                        charts and report screenshots
```

---

## 🔁 Reproduce it yourself (fully free, no API keys)

```bash
# 1. Install the CoEval framework
git clone https://github.com/ApartsinProjects/CoEval.git && cd CoEval
python -m pip install -e .

# 2. Pull the local models (Ollama)
ollama pull llama3:8b   gemma2:2b   gemma2:9b
ollama pull qwen2.5:3b  qwen2.5:7b  phi3   mistral:7b

# 3. Probe → plan → run → analyze
coeval probe   --config config/cybersecurity_runC.yaml
coeval plan    --config config/cybersecurity_runC.yaml
coeval run     --config config/cybersecurity_runC.yaml
coeval analyze all --run Runs/cybersecurity-run-C-large --out reports
```

> On a memory-limited machine, set `OLLAMA_MAX_LOADED_MODELS=1` so only one model is resident at a time — see [scripts/](scripts/) for the resilient overnight runner we used.

---

## 🙏 Acknowledgements

The **CoEval** framework and paper are the work of **Dr. Alexander Apartsin** and **Dr. Yehudit Aperstein** — <https://github.com/ApartsinProjects/CoEval>. All experiment configurations, runs, analyses, figures, and documentation in this repository are the student capstone work built **on top of** that framework.
