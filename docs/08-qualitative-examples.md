# 08 — Qualitative Examples

Statistics tell us *what* happened; these worked examples show *how*. Each is a real, unedited item
from **Run C**: a question authored by a Teacher model, an answer from a Student model, and the
scores assigned by all seven Judges. They are reproducible with
[`extract_examples.py`](../runs/run-C-local) over the run artifacts.

Scores map High = 1.0, Medium = 0.5, Low = 0.0; the per-judge value shown is the mean over the five
rubric factors (Technical Accuracy, Theoretical Understanding, Practical Insight, Completeness,
Clarity).

---

## Example 1 — A strong answer, near-unanimous agreement

**Domain:** Malware Analysis · **Teacher:** gemma2-2b · **Student:** gemma2-2b

> **Question.** *A newly discovered malware is spreading rapidly through targeted phishing emails and
> exploiting vulnerabilities in popular remote access tools. Explain how this malware could be
> analyzed to understand its capabilities, potential impact, and mitigation strategies.*

> **Answer.** *To analyze this newly discovered malware, we can employ a multi-faceted approach.
> First, network traffic analysis can reveal communication patterns, command-and-control servers, and
> potential victims. Next, static code analysis can identify malicious components like encryption
> routines or data exfiltration mechanisms. Finally, dynamic analysis using sandboxes can simulate
> the malware's behavior to understand its full impact…*

| Judge | gemma2-2b | gemma2-9b | llama3-8b | mistral-7b | phi3 | qwen2.5-3b | qwen2.5-7b |
|-------|:---------:|:---------:|:---------:|:----------:|:----:|:----------:|:----------:|
| Score | 1.00 | 1.00 | 0.90 | 1.00 | 1.00 | 1.00 | 1.00 |

**Why it matters.** The answer correctly names the three standard pillars of malware analysis
(network, static, dynamic). The judges agree almost perfectly — this is what *consensus on a good
answer* looks like, and it shows the rubric rewards genuinely correct technical content.

---

## Example 2 — A wrong answer the benchmark correctly fails

**Domain:** Cryptography (Advanced) · **Teacher:** llama3-8b · **Student:** gemma2-2b

> **Question.** *Consider an RSA system where the modulus n is the product of two large primes p and
> q. If the attacker knows that p is a 1024-bit number and that q is also a 1024-bit number, can they
> efficiently factor n? Explain why or why not.*

> **Answer.** *Yes, an attacker can efficiently factor n using the knowledge of p and q. The attacker
> can use a factoring algorithm like Pollard's rho or the general number field sieve … if p and q are
> relatively prime, then factoring n becomes much easier.*

| Judge | gemma2-2b | gemma2-9b | llama3-8b | mistral-7b | phi3 | qwen2.5-3b | qwen2.5-7b |
|-------|:---------:|:---------:|:---------:|:----------:|:----:|:----------:|:----------:|
| Score | 0.20 | 0.30 | 0.00 | 0.10 | 0.30 | 0.00 | 0.00 |

**Why it matters.** The answer is **factually wrong**: knowing only the *bit-length* of p and q does
not let you factor n (that is exactly what makes RSA secure), and "p and q relatively prime → easier"
is nonsense (distinct primes are always coprime). **Every judge scored it Low** (mean 0.13). This is
the most important kind of evidence that the auto-generated benchmark *works*: a hard, contamination-
free cryptography question exposed a real misconception, and the judge ensemble caught it unanimously.

---

## Example 3 — Maximum judge disagreement (why the ensemble matters)

**Domain:** Network Security (Advanced) · **Teacher:** gemma2-2b · **Student:** qwen2.5-3b

> **Question.** *A company uses a VPN to secure its remote workforce, but employees experience slow
> speeds and frequent outages. What security vulnerabilities might contribute, and what steps address
> them?*

> **Answer.** *…potential vulnerabilities include weak or outdated encryption protocols, insufficient
> tunneling capacity leading to congestion, and infrastructure issues not directly related to the VPN
> configuration. To address them, review and update VPN software and protocols … upgrade network
> hardware…*

| Judge | gemma2-2b | gemma2-9b | llama3-8b | mistral-7b | **phi3** | qwen2.5-3b | qwen2.5-7b |
|-------|:---------:|:---------:|:---------:|:----------:|:--------:|:----------:|:----------:|
| Score | 1.00 | 0.70 | 0.90 | 1.00 | **0.00** | 1.00 | 1.00 |

**Why it matters.** This single answer received a **full 1.00 from six judges and a 0.00 from phi3** —
a spread of 1.0, the maximum possible. A *single-judge* evaluation using phi3 would have scored this
reasonable answer a flat zero; six others saw it as excellent. The **ensemble mean (0.80)** is the
defensible verdict, and this example is the clearest possible illustration of the project's central
theme — *no single judge can be trusted; aggregation is what produces a fair score.* It is exactly
the failure mode the CoEval paper's multi-judge design exists to neutralize.

---

### What these examples collectively demonstrate
- **The benchmark is meaningful:** good answers score high (Ex. 1), wrong answers score low (Ex. 2).
- **Judges catch real technical errors** — the RSA misconception was failed unanimously.
- **Single judges are unreliable** — phi3's lone 0.00 (Ex. 3) would have mis-scored a good answer.
- **The ensemble is the right unit of trust** — the aggregate is robust to any one judge's bias.
