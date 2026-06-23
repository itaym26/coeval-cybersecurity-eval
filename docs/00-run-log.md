# 00 — Complete Run Log

This document records **every** experiment run we executed, in chronological order. It is
intentionally exhaustive: the failed iterations are part of the project's story, showing how the
configuration was diagnosed and corrected step by step until a clean result was obtained. Each entry
states whether the run **succeeded or failed, the cause, the conclusion, and the action taken next**.

The runs cluster into three phases of the project:
- **Iteration phase (Runs 01–04):** rapid failures that mapped out the constraints of free model APIs.
- **Run A (Run 05):** the first usable result — a partial cloud run.
- **Run B (local):** the first complete, reproducible ranking.
- **Run C (planned):** the final large-scale quality run.

---

## Summary table

| # | Run ID | Tier | Models | Result | Root cause / outcome |
|---|--------|------|--------|--------|----------------------|
| 01 | `cybersecurity-run-01` | Cloud | llama-3.3-70b, gemini-2.0-flash, mistral-7b, qwen-2.5-72b | ❌ Failed | `llama-3.3-70b:free` rate-limited (HTTP 429) in Phase 1 |
| 02 | `cybersecurity-run-02` | Cloud | deepseek-chat + 3 | ❌ Failed | `deepseek-chat:free` no longer free (HTTP 404) |
| 03 | `cybersecurity-run-03` | Cloud+local | llama3-8b(local), gemini, mistral, qwen | ❌ Failed | `gemini-2.0-flash-exp:free` removed from OpenRouter (HTTP 404) |
| 04 | `cybersecurity-run-04` | Cloud+local | llama3-8b, gpt-oss-20b, gemma-4-31b, qwen3-next-80b | ❌ Failed | `qwen3-next-80b:free` rate-limited (HTTP 429) in Phase 1 |
| 05 | `cybersecurity-run-05` (**Run A**) | Cloud+local | llama3-8b, gpt-oss-20b, gemma-4-31b, nemotron-nano-9b | ⚠️ Partial success | Completed Phases 1–3; Phase 4–5 hit the **50-requests/day** account cap. Yielded a valid 2-model ranking. |
| B | `cybersecurity-run-B-local` (**Run B**) | Local | llama3-8b, gemma2-2b, qwen2.5-3b, phi3 | ✅ Success | Complete 4-model ranking, 764/768 valid (99%). Winner: phi3 (3.8B) > llama3-8b (8B). ~3.5 h on 13.7 GB RAM with single-model loading. |
| C | `cybersecurity-run-C-large` (**Run C**) | Local | 7 models (incl. gemma2 2b/9b, qwen2.5 3b/7b size pairs), 20 questions | 🔄 Running | Final large-scale run (~8,000 calls, several nights). First launch aborted on a `--continue` flag misuse; relaunched without it and running. |

---

## Detailed entries

### Run 01 — first cloud attempt
- **Config:** four OpenRouter `:free` models (Meta, Google, Mistral, Alibaba), 12 datapoints.
- **Result:** ❌ Failed in Phase 1 (attribute mapping).
- **Cause:** `meta-llama/llama-3.3-70b-instruct:free` returned HTTP 429 — "temporarily rate-limited
  upstream" (routed through the Venice provider).
- **Conclusion:** Popular free models are heavily contended and rate-limited.
- **Next action:** Swap the rate-limited model for a different free model.

### Run 02 — DeepSeek swap
- **Change:** replaced `llama-3.3-70b` with `deepseek-chat:free`.
- **Result:** ❌ Failed immediately.
- **Cause:** HTTP 404 — "This model is unavailable for free. The paid version is available now."
  The free DeepSeek slug had been retired.
- **Conclusion:** Free model availability is volatile; slugs disappear without notice.
- **Next action:** Use a locally-hosted model (Ollama) for reliability; verify remaining slugs.

### Run 03 — first local model introduced
- **Change:** replaced DeepSeek with local `llama3:8b` (Ollama).
- **Result:** ❌ Failed in Phase 1.
- **Cause:** `google/gemini-2.0-flash-exp:free` returned HTTP 404 — "No endpoints found." Another
  retired free slug. (The local llama3 model itself worked correctly.)
- **Conclusion:** Local inference is reliable; the remaining cloud slugs must be re-verified against
  the live model list.
- **Next action:** Query `coeval models` for currently-valid `:free` slugs and rebuild the pool.

### Run 04 — verified free slugs + back-off patch
- **Change:** rebuilt the cloud pool with verified `:free` models (gpt-oss-20b, gemma-4-31b,
  qwen3-next-80b) alongside local llama3-8b.
- **Result:** ❌ Failed in Phase 1.
- **Cause:** `qwen3-next-80b:free` rate-limited (HTTP 429, `Retry-After ≈ 30s`). We discovered the
  client's back-off was only 1–2 s — far too short for the 30 s window.
- **Conclusion:** The retry logic must honor the provider's `Retry-After` header.
- **Next action:** Patch `openrouter_iface.py` to wait ~30 s / up to 6 attempts, and swap qwen3 for
  NVIDIA `nemotron-nano-9b`.

### Run 05 — Run A (first usable result)
- **Change:** back-off patch applied; final cloud pool (llama3-8b, gpt-oss-20b, gemma-4-31b,
  nemotron-nano-9b).
- **Result:** ⚠️ **Partial success.** Phases 1–3 completed fully (48 questions, 19-factor rubric);
  Phases 4–5 partially completed (194/384 valid judgments).
- **Cause of incompleteness:** OpenRouter's **account-wide 50-requests/day** free cap — a hard wall
  no client change can bypass.
- **Conclusion:** A valid 2-model ranking was obtained (`gpt-oss-20b` 0.919 > `llama3-8b` 0.775), and
  judge-bias was measured. Free cloud tiers cannot sustain a full ensemble run.
- **Next action:** Run fully local (Run B). Full analysis in [`03-run-A-findings.md`](03-run-A-findings.md).

### Run B — first complete local run
- **Config:** four local models (llama3-8b, gemma2-2b, qwen2.5-3b, phi3), 12 datapoints.
- **First attempt:** ❌ failed Phase 1 — small models could not emit the complex JSON that `auto`
  attribute/rubric generation requires (every teacher failed JSON parsing).
- **Fix:** supplied explicit attributes and a compact 5-factor rubric (distilled from Run A); set an
  absolute `storage_folder`.
- **Result:** 🔄 Phases 1–4 complete (all 16 response sets); Phase 5 at 10/16 when the PC was
  rebooted. Resuming overnight via `--continue` with `OLLAMA_MAX_LOADED_MODELS=1` (the 13.7 GB
  machine froze when four models loaded simultaneously).
- **Result:** ✅ **Complete success.** All phases finished; 764/768 valid judgments (99%). Final
  ranking: phi3 0.898 > llama3-8b 0.860 > qwen2.5-3b 0.856 > gemma2-2b 0.798.
- **Conclusion:** Local inference removes the rate-limit wall (and raised validity from 51% to 99%);
  memory, not quota, was the constraint, solved by loading one model at a time. Key finding: the
  3.8B phi3 beat the 8B llama3 — bigger is not always better. Consensus ranking stable across all
  judges. Full analysis in [`04-run-B-findings.md`](04-run-B-findings.md).
- **Next action:** Build the large-scale Run C (~7 models, ~20 questions) to confirm these findings
  at scale.

### Run C — final large-scale run
- **Goal:** demonstrate that CoEval scales — a single large, high-quality run over **7 local models
  and 20 questions** (980 responses, ~6,900 judgments, ~8,000 total calls), including same-family
  size pairs (gemma2 2b↔9b, qwen2.5 3b↔7b) for a size-vs-performance analysis.
- **Models:** llama3:8b (Meta), gemma2:2b + gemma2:9b (Google), qwen2.5:3b + qwen2.5:7b (Alibaba),
  phi3 (Microsoft), mistral:7b (Mistral) — five vendors.
- **Execution:** spans several nights. RAM kept safe via `OLLAMA_MAX_LOADED_MODELS=1` (one model in
  memory at a time); checkpointing lets each night resume with `--continue`.

- **Launch incident (resolved):** the very first launch was issued with `--continue` and aborted
  immediately:
  > `--continue specified but no existing experiment found ... (meta.json is missing)`

  **Cause:** `--continue` resumes an *existing* experiment, but this was the first run, so there was
  nothing to resume.
  **Conclusion:** the first launch of any experiment must omit `--continue`; only subsequent resumes
  use it.
  **Action taken:** relaunched without `--continue` (started cleanly), and hardened
  `scripts/run_C_overnight.ps1` to auto-detect `meta.json` — it now omits `--continue` on the first
  night and adds it automatically on later nights. The run then proceeded normally into Phase 3.
- **Purpose:** the capstone result, and the final step in the project's evolution from small
  exploratory runs to one large, authoritative ranking. Full analysis will be added once complete.
