# Scripts — how each run was launched

This folder documents and automates how the three experiments were executed.

| Run | Config | How it was launched |
|-----|--------|---------------------|
| **A** (cloud) | [`config/cybersecurity_cloud.yaml`](../config/cybersecurity_cloud.yaml) | Direct CLI commands (see below) — no persistent script needed |
| **B** (local) | [`config/cybersecurity_local.yaml`](../config/cybersecurity_local.yaml) | [`run_B_overnight.ps1`](run_B_overnight.ps1) |
| **C** (local, large) | [`config/cybersecurity_runC.yaml`](../config/cybersecurity_runC.yaml) | [`run_C_overnight.ps1`](run_C_overnight.ps1) |

## Why Run A has no script

Run A was a **cloud** run over OpenRouter free-tier models. It was short and was launched with the
standard CoEval command sequence directly — it never needed the resilient overnight runner that the
multi-hour **local** runs (B and C) require. For completeness, this is exactly how Run A was run:

```bash
coeval probe --config config/cybersecurity_cloud.yaml   # verify models reachable (no cost)
coeval plan  --config config/cybersecurity_cloud.yaml   # estimate calls / cost
coeval run   --config config/cybersecurity_cloud.yaml   # execute (hit the 50-req/day free cap → partial)
coeval analyze all --run Runs/cybersecurity-run-05 --out reports
```

(Run A's outcome and the rate-limit wall it exposed are documented in
[`docs/03-run-A-findings.md`](../docs/03-run-A-findings.md).)

## The overnight scripts (B and C)

The local runs are long (hours for B, multiple sessions for C) and must survive a memory-limited
laptop. Both scripts therefore:

1. set `OLLAMA_MAX_LOADED_MODELS=1` so only one model is resident at a time (prevents the RAM freeze);
2. apply a comprehensive no-sleep power policy for the duration of the run;
3. launch `coeval run` (the Run C script auto-detects `meta.json` and adds `--continue` to resume).

```powershell
# Run B
powershell -ExecutionPolicy Bypass -File scripts/run_B_overnight.ps1
# Run C (re-run on subsequent sessions; it resumes from the checkpoint)
powershell -ExecutionPolicy Bypass -File scripts/run_C_overnight.ps1
```

Analysis scripts (rankings, statistics, example extraction) live alongside each run's data under
[`runs/`](../runs/).
