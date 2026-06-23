# Evaluating Free Large Language Models on Cybersecurity Knowledge with CoEval

**An ensemble-based, label-free benchmarking study using the CoEval framework**

> Final capstone project — Large Language Models course
> Domain under evaluation: **Cybersecurity knowledge and reasoning**

---

## 1. Abstract

This project applies **[CoEval](https://github.com/ApartsinProjects/CoEval)** — an ensemble-based,
self-evaluation framework for ranking Large Language Models (LLMs) without labeled data — to the
domain of **cybersecurity**. Using a pool of freely available models (local models served through
[Ollama](https://ollama.com) and free-tier models accessed through [OpenRouter](https://openrouter.ai)),
we let the models collaboratively generate a contamination-free benchmark, answer one another's
questions, and score one another's answers. We then analyze the resulting rankings, judge-agreement
statistics, and bias signals.

The study is intentionally structured around **two complementary experimental runs**:

| Run | Provider tier | Status | Purpose |
|-----|---------------|--------|---------|
| **Run A** | Cloud free-tier (OpenRouter `:free` + 1 local) | Partial (rate-limited) | Reveals the practical limits of free cloud APIs and yields a 2-model student ranking |
| **Run B** | Fully local (Ollama) | Complete | A reproducible, no-rate-limit, end-to-end 4-model ranking |

A central methodological finding emerges already in Run A: **individual judges exhibit measurable
self-preference and divergent strictness**, which is precisely the bias that CoEval's multi-judge
ensemble is designed to dampen.

---

## 2. What is CoEval? (framework overview)

CoEval ranks models for a *custom* task when (a) no task-specific labeled data exists, and
(b) public benchmarks cannot be trusted because their items may have leaked into model
pre-training. It does so by assigning every model three **rotating roles**:

| Role | Responsibility |
|------|----------------|
| **Teacher** | Generates synthetic, contamination-free benchmark questions for the domain |
| **Student** | Answers the questions — this is the behavior being measured |
| **Judge** | Scores student answers against an automatically generated rubric |

The pipeline runs in **five checkpointed phases**:

1. **Attribute mapping** — infer the dimensions of the domain (e.g. sub-topics, difficulty).
2. **Rubric mapping** — derive the scoring criteria automatically.
3. **Data generation** — each teacher produces a set of questions.
4. **Response collection** — each student answers every teacher's questions.
5. **Evaluation** — each judge scores every response, producing an ensemble ranking.

For a deeper conceptual treatment see [`docs/02-methodology.md`](docs/02-methodology.md).

---

## 3. Why cybersecurity?

Cybersecurity is a strong differentiator for LLM evaluation because correct answers require a
combination of: precise terminology, conceptual understanding (CIA triad, cryptography, attack
taxonomies), applied reasoning over scenarios, and awareness of defensive best practice. Models of
different sizes and vendors tend to show clear, measurable gaps on this material. The domain
background we studied before running the experiments is documented in
[`docs/01-domain-background.md`](docs/01-domain-background.md).

---

## 4. Repository structure

```
coeval-cybersecurity-eval/
├── README.md                       This file
├── config/
│   ├── cybersecurity_cloud.yaml    Run A configuration (cloud free-tier)
│   └── cybersecurity_local.yaml    Run B configuration (local Ollama)
├── runs/
│   ├── run-A-cloud-free/           Run A outputs, reports, screenshots
│   └── run-B-local/                Run B outputs, reports, screenshots
├── docs/
│   ├── 00-run-log.md               Chronological log of every run (success/failure + cause)
│   ├── 01-domain-background.md     Cybersecurity concepts primer
│   ├── 02-methodology.md           CoEval mechanics + our configuration
│   ├── 03-run-A-findings.md        Run A results and analysis
│   ├── 04-run-B-findings.md        Run B results and analysis
│   └── 05-conclusions.md           Comparative conclusions
└── figures/                        Charts and report screenshots
```

---

## 5. How to reproduce

```bash
# 1. Install the CoEval framework
git clone https://github.com/ApartsinProjects/CoEval.git
cd CoEval
python -m pip install -e .

# 2. (Run B, recommended) install Ollama and pull the local models
ollama pull llama3:8b
ollama pull gemma2:2b
ollama pull qwen2.5:3b
ollama pull phi3

# 3. Validate connectivity, estimate cost, then run
coeval probe --config config/cybersecurity_local.yaml
coeval plan  --config config/cybersecurity_local.yaml
coeval run   --config config/cybersecurity_local.yaml

# 4. Generate all analysis reports
coeval analyze all --run Runs/cybersecurity-run-B-local --out reports
```

> **Note on the cloud run (Run A):** OpenRouter's free tier is capped at **50 requests/day and
> 16 requests/minute account-wide**, shared across all `:free` models. This is incompatible with a
> full CoEval run (~1,000 calls) and is the reason Run A is partial. See
> [`docs/03-run-A-findings.md`](docs/03-run-A-findings.md) for the full account.

---

## 6. Key results (summary)

*Run A (cloud free-tier, partial)* — student ranking over 194 valid judgments:

| Rank | Model | Mean normalized score |
|------|-------|-----------------------|
| 🥇 | gpt-oss-20b | 0.919 |
| 🥈 | llama3-8b | 0.775 |

*Run B (local, complete)* — full four-model ranking over 764 valid judgments (99%):

| Rank | Model | Vendor | Size | Mean normalized score |
|------|-------|--------|------|-----------------------|
| 🥇 | phi3 | Microsoft | 3.8B | 0.898 |
| 🥈 | llama3-8b | Meta | 8B | 0.860 |
| 🥉 | qwen2.5-3b | Alibaba | 3B | 0.856 |
| 4 | gemma2-2b | Google | 2B | 0.798 |

Headline finding: **bigger is not always better** — the 3.8B `phi3` outscored the 8B `llama3-8b`.
The consensus ranking was stable across all four judges. See
[`docs/04-run-B-findings.md`](docs/04-run-B-findings.md).

Final comparative conclusions are in [`docs/05-conclusions.md`](docs/05-conclusions.md).

---

## 7. Acknowledgements

The CoEval framework was created by the course instructor and is available at
<https://github.com/ApartsinProjects/CoEval>. All evaluation runs, configurations, analyses, and
documentation in this repository are the student work product of this capstone.
