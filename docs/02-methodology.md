# 02 — Methodology: CoEval Mechanics and Our Configuration

## 1. The CoEval pipeline in detail

CoEval implements an **ensemble self-evaluation** in which a pool of models is assessed without any
human labels. Every model in the pool can act in three rotating roles — **Teacher**, **Student**,
and **Judge** — and the system executes five independently checkpointed phases.

### Phase 1 — Attribute mapping
Each Teacher infers the dimensions that structure the domain. Two attribute layers are produced:

- **Target attributes** — the substantive axes of variation (sub-topics, difficulty, depth) that
  drive *coverage* of the domain.
- **Nuanced attributes** — surface-level variation (phrasing, tone, document structure) that
  prevents the generated dataset from collapsing into a single style.

### Phase 2 — Rubric mapping
The Teachers collectively derive the **scoring rubric**: the named criteria against which answers
will later be judged. Like the attributes, the rubric is generated automatically from the task
description.

### Phase 3 — Data generation
Each Teacher generates a set of **datapoints** (question + reference answer), sampling across the
attribute space so the benchmark covers the domain. Because the items are freshly synthesized, they
are **contamination-free** — they cannot have leaked into any model's pre-training.

### Phase 4 — Response collection
Each **Student** answers every Teacher's questions. These answers are the behavior being measured.

### Phase 5 — Evaluation
Each **Judge** scores every student response against the rubric. Aggregating across multiple judges
yields an **ensemble ranking** that is more robust than any single judge's opinion.

---

## 2. Our task definition

We configured a single task, `cybersecurity`, with the following description given to the framework:

> *Cybersecurity knowledge and reasoning assessment. Given a cybersecurity scenario, concept, or
> technical question, the model must provide accurate, technically sound answers covering topics
> such as network attacks, web vulnerabilities, cryptographic concepts, malware behavior, and
> defensive security practices. Responses should demonstrate both theoretical understanding and
> practical reasoning ability.*

The two runs differ deliberately in **how the benchmark is provisioned**:

- **Run A (cloud)** supplied **`target_attributes: auto`**, **`nuanced_attributes: auto`**, and
  **`rubric: auto`** — delegating the entire benchmark design to the framework. This tests CoEval's
  automatic-provisioning capability and removes designer bias from the question set.
- **Run B (local)** supplied **explicit** attributes and a **compact 5-factor rubric** instead of
  `auto`. This was a necessary adaptation: the small local models (2B–8B) could not reliably emit
  the large, deeply-nested JSON that auto attribute/rubric generation requires — in an early Run B
  attempt every teacher failed JSON parsing on `target_attributes`, stalling Phase 1. Providing
  static values makes Phases 1–2 deterministic and reproducible, and lets the small models focus on
  the tasks they handle well (generating questions, answering, and scoring). The Run B rubric is a
  5-factor distillation of Run A's auto-generated 19 factors, which also makes the two runs more
  directly comparable.

---

## 3. What the framework produced automatically

### Target attributes (Phase 1, excerpt)
The Teachers independently produced a domain structure that maps cleanly onto standard
cybersecurity taxonomy, including:

- `domain`: *Network Security, Web Application Security, Cryptography, Malware Analysis, Incident
  Response, Identity and Access Management, Cloud Security, Governance/Risk/Compliance*
- `vulnerability_type`: *network_attack, web_vulnerability, cryptographic_flaw, malware_behavior,
  defensive_practice*
- `scenario_type`: *Threat Hunting, Vulnerability Assessment, Forensic Investigation, Red Teaming, …*
- `complexity_level`: *Fundamental, Intermediate, Advanced, Expert*

That the framework recovered this structure on its own is itself a positive result for automatic
attribute mapping (cross-reference [`01-domain-background.md`](01-domain-background.md)).

### Rubric (Phase 2)
The merged rubric contained **19 scoring factors**, the most salient being: *Accuracy*, *Technical
Accuracy*, *Theoretical Understanding*, *Technical Terminology*, *Practical Insight*, *Reasoning and
Depth*, *Completeness*, *Clarity*, and *Conciseness/Structure*. These are exactly the qualities a
human cybersecurity expert would weigh — strong evidence that automatic rubric mapping captured the
domain's evaluation standards. Judges scored each factor on a three-level ordinal scale
(**High / Medium / Low**), which we map to numeric values (1.0 / 0.5 / 0.0) for analysis.

---

## 4. Model pool

Two model pools were used across the two runs. All models are **free to use**.

### Run A — cloud free-tier (+ one local)
| Model name | Vendor | Provider |
|------------|--------|----------|
| `llama3-8b` | Meta | Ollama (local) |
| `gpt-oss-20b` | OpenAI | OpenRouter `:free` |
| `gemma-4-31b` | Google | OpenRouter `:free` |
| `nemotron-nano-9b` | NVIDIA | OpenRouter `:free` |

### Run B — fully local
| Model name | Vendor | Size | Provider |
|------------|--------|------|----------|
| `llama3-8b` | Meta | 8B | Ollama |
| `gemma2-2b` | Google | 2B | Ollama |
| `qwen2.5-3b` | Alibaba | 3B | Ollama |
| `phi3` | Microsoft | 3.8B | Ollama |

In both pools every model is assigned all three roles (`roles: [teacher, student, judge]`), giving
the full rotating-role design. Each Teacher generates `total: 12` datapoints.

---

## 5. Operational procedure

For every run we followed the framework's recommended sequence:

```bash
coeval probe --config <config>.yaml   # verify every model is reachable (no cost)
coeval plan  --config <config>.yaml   # estimate calls / cost / time
coeval run   --config <config>.yaml   # execute all five phases
coeval analyze all --run <run_dir> --out reports   # build HTML + Excel reports
```

Runs are checkpointed: an interrupted run can be resumed with `coeval run --continue` without
repeating completed work — a property we relied on heavily given the free-tier constraints
documented in [`03-run-A-findings.md`](03-run-A-findings.md).

---

## 6. A framework adaptation for the free tier

The stock OpenRouter interface retried failed calls with a 1–2 second back-off. Free-tier models
return HTTP 429 with a `Retry-After` of ~30 seconds, so the original back-off exhausted all retries
before the rate-limit window cleared. We modified
`Code/runner/interfaces/openrouter_iface.py` to **honor the `Retry-After` header** (waiting up to
~30 s, up to 6 attempts). This is documented transparently as an adaptation for free-tier operation;
it does not change any evaluation logic. It mitigates *per-minute* limits but cannot overcome the
*per-day* account cap, which is the fundamental constraint discussed in the Run A findings.
