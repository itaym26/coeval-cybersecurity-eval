# ============================================================
#  Run B — overnight completion script (RAM-safe)
#  Finishes the remaining CoEval Phase 5 judging for the
#  fully-local cybersecurity experiment without freezing the PC.
#
#  Usage (just double-click won't work — run from PowerShell):
#     powershell -ExecutionPolicy Bypass -File C:\Users\itaym\CoEval\run_B_overnight.ps1
# ============================================================

$ErrorActionPreference = "Continue"
$ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Output "[$ts] Starting Run B overnight completion..."

# 1) Make coeval reachable on PATH
$env:PATH += ";C:\Users\itaym\AppData\Local\Programs\Python\Python312\Scripts"

# 2) Cap Ollama memory: load only ONE model at a time (prevents the freeze
#    seen when 4 local models loaded into 13.7 GB RAM simultaneously).
$env:OLLAMA_MAX_LOADED_MODELS = "1"
$env:OLLAMA_NUM_PARALLEL      = "1"

# Restart the Ollama server so it picks up the new limits.
Write-Output "[$(Get-Date -Format HH:mm:ss)] Restarting Ollama with single-model limit..."
Get-Process ollama* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden -ErrorAction SilentlyContinue
Start-Sleep -Seconds 5

# 3) Keep the machine awake for the whole run (no sleep / no display-off).
#    Saves current scheme so we can restore it afterwards.
Write-Output "[$(Get-Date -Format HH:mm:ss)] Disabling sleep for the duration of the run..."
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg /change monitor-timeout-ac 0

# 4) Continue the run — resumes from the saved checkpoint, only the missing
#    Phase 5 judgments are generated.
Set-Location "C:\Users\itaym\CoEval"
Write-Output "[$(Get-Date -Format HH:mm:ss)] Resuming CoEval (coeval run --continue)..."
coeval run --config "C:\Users\itaym\CoEval\cybersecurity_runB.yaml" --continue *>> "C:\Users\itaym\CoEval\Runs\run-B-overnight.log"

$exit = $LASTEXITCODE
Write-Output "[$(Get-Date -Format HH:mm:ss)] CoEval finished (exit code $exit)."

# 5) Restore normal power behavior (sleep after 30 min again).
powercfg /change standby-timeout-ac 30
powercfg /change monitor-timeout-ac 10
Write-Output "[$(Get-Date -Format HH:mm:ss)] Power settings restored. Done. Full log: Runs\run-B-overnight.log"
