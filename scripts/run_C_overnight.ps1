# ============================================================
#  Run C — overnight script (RAM-safe, resumable)
#  Runs / resumes the final large-scale CoEval run:
#  7 local models, 20 questions. Designed to be run on
#  multiple consecutive nights — each run resumes from the
#  saved checkpoint via --continue until the experiment is done.
#
#  Usage (from PowerShell):
#     powershell -ExecutionPolicy Bypass -File C:\Users\itaym\CoEval\run_C_overnight.ps1
# ============================================================

$ErrorActionPreference = "Continue"
Write-Output "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Starting Run C (large-scale) ..."

# 1) coeval on PATH
$env:PATH += ";C:\Users\itaym\AppData\Local\Programs\Python\Python312\Scripts"

# 2) One model in memory at a time (prevents the 13.7 GB freeze).
$env:OLLAMA_MAX_LOADED_MODELS = "1"
$env:OLLAMA_NUM_PARALLEL      = "1"

Write-Output "[$(Get-Date -Format HH:mm:ss)] Restarting Ollama with single-model limit..."
Get-Process ollama* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden -ErrorAction SilentlyContinue
Start-Sleep -Seconds 5

# 3) Keep the machine awake for the whole run.
Write-Output "[$(Get-Date -Format HH:mm:ss)] Disabling sleep..."
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg /change monitor-timeout-ac 0

# 4) Run (first night) or resume (subsequent nights).
#    --continue ONLY works once the experiment exists (meta.json present);
#    on the very first run it must be omitted, or CoEval errors out.
Set-Location "C:\Users\itaym\CoEval"
$meta = "C:\Users\itaym\CoEval\Runs\cybersecurity-run-C-large\meta.json"
if (Test-Path $meta) {
    Write-Output "[$(Get-Date -Format HH:mm:ss)] Existing experiment found — resuming (coeval run --continue)..."
    coeval run --config "C:\Users\itaym\CoEval\cybersecurity_runC.yaml" --continue *>> "C:\Users\itaym\CoEval\Runs\run-C-overnight.log"
} else {
    Write-Output "[$(Get-Date -Format HH:mm:ss)] No experiment yet — starting fresh (coeval run)..."
    coeval run --config "C:\Users\itaym\CoEval\cybersecurity_runC.yaml" *>> "C:\Users\itaym\CoEval\Runs\run-C-overnight.log"
}

$exit = $LASTEXITCODE
Write-Output "[$(Get-Date -Format HH:mm:ss)] CoEval finished this session (exit code $exit)."

# 5) Restore normal power behavior.
powercfg /change standby-timeout-ac 30
powercfg /change monitor-timeout-ac 10
Write-Output "[$(Get-Date -Format HH:mm:ss)] Power restored. If the run is not yet complete, just run this script again the next night. Log: Runs\run-C-overnight.log"
