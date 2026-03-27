#Requires -Version 5.1
# Skip GDFold2 entirely. Only SPIRED-Stab (WT vs each mutant) + stability_summary.csv.
# Requires: conda env spired_fitness; SPIRED-Fitness\model\ weights.
# Prepare inputs: python prepare_bri1_inputs.py
# Usage: .\run_bri1_stab_only.ps1

$ErrorActionPreference = "Stop"

if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    throw "conda not found. Install Miniconda/Anaconda and run: conda init powershell"
}

$Here = $PSScriptRoot
$Root = Split-Path -Parent $Here
$Spired = Join-Path $Root 'SPIRED-Fitness'
$In = Join-Path $Here 'input'

if (-not (Test-Path -LiteralPath $Spired)) {
    throw "SPIRED-Fitness not found: $Spired"
}

$pair0 = Join-Path $In 'WT_vs_S662F.fasta'
if (-not (Test-Path -LiteralPath $pair0)) {
    throw "Missing input. Run first: python prepare_bri1_inputs.py"
}

function Invoke-SpiredStab {
    param([string]$Fasta, [string]$OutDir)
    Write-Host "== SPIRED-Stab: $Fasta -> $OutDir ==" -ForegroundColor Cyan
    $py = Join-Path $Spired 'run_SPIRED-Stab.py'
    & conda run -n spired_fitness --no-capture-output python $py --fasta_file $Fasta --saved_folder $OutDir
    if ($LASTEXITCODE -ne 0) { throw "SPIRED-Stab failed (exit $LASTEXITCODE)" }
}

foreach ($tag in @("S662F", "P719L", "T750I")) {
    $pair = Join-Path $In "WT_vs_$tag.fasta"
    $stabOut = Join-Path $Here "stability_WT_vs_$tag"
    New-Item -ItemType Directory -Force -Path $stabOut | Out-Null
    Invoke-SpiredStab -Fasta $pair -OutDir $stabOut
}

Write-Host "== stability_summary.csv ==" -ForegroundColor Cyan
$collector = Join-Path $Here 'collect_stability_summary.py'
& python $collector
if ($LASTEXITCODE -ne 0) { throw "collect_stability_summary failed" }

Write-Host 'Done. See stability_WT_vs_*\pred.csv and stability_summary.csv (no GDFold2 / full-atom).' -ForegroundColor Green
