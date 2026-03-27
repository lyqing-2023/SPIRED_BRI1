#Requires -Version 5.1
# Windows: run full bri1_results pipeline (same as run_bri1_spired.sh).
# Requires conda envs: spired_fitness, gdfold2; models in SPIRED-Fitness\model\
# If you cannot install GDFold2: use run_bri1_stab_only.ps1 (Stab + summary only).
# Usage: .\run_bri1_spired.ps1
#        .\run_bri1_spired.ps1 -GdfoldDevice cuda:0

param(
    [string]$GdfoldDevice = "cpu"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    throw "conda not found. Install Miniconda/Anaconda and run: conda init powershell"
}

$Here = $PSScriptRoot
$Root = Split-Path -Parent $Here
$Spired = Join-Path $Root 'SPIRED-Fitness'
$In = Join-Path $Here 'input'
$GdfoldDir = Join-Path $Spired 'scripts\GDFold2'

if (-not (Test-Path -LiteralPath $Spired)) {
    throw "SPIRED-Fitness not found: $Spired"
}

$fitnessIn = Join-Path $In 'bri1_550-800_fitness.fasta'
if (-not (Test-Path -LiteralPath $fitnessIn)) {
    throw "Missing input. Run first: python prepare_bri1_inputs.py"
}

$fitnessOut = Join-Path $Here 'fitness'
New-Item -ItemType Directory -Force -Path $fitnessOut | Out-Null

function Invoke-SpiredFitness {
    param([string]$Fasta, [string]$OutDir)
    Write-Host "== SPIRED-Fitness ==" -ForegroundColor Cyan
    $py = Join-Path $Spired 'run_SPIRED-Fitness.py'
    & conda run -n spired_fitness --no-capture-output python $py --fasta_file $Fasta --saved_folder $OutDir
    if ($LASTEXITCODE -ne 0) { throw "SPIRED-Fitness failed (exit $LASTEXITCODE)" }
}

function Invoke-Gdfold2Pair {
    param([string]$Fasta, [string]$OutDir)
    Write-Host "== GDFold2: $OutDir ==" -ForegroundColor Cyan
    Push-Location -LiteralPath $GdfoldDir
    try {
        & conda run -n gdfold2 --no-capture-output python fold.py $Fasta $OutDir -d $GdfoldDevice
        if ($LASTEXITCODE -ne 0) { throw "GDFold2 fold failed (exit $LASTEXITCODE)" }
        & conda run -n gdfold2 --no-capture-output python relax.py --input $Fasta --output $OutDir
        if ($LASTEXITCODE -ne 0) { throw "GDFold2 relax failed (exit $LASTEXITCODE)" }
    }
    finally {
        Pop-Location
    }
}

function Invoke-SpiredStab {
    param([string]$Fasta, [string]$OutDir)
    Write-Host "== SPIRED-Stab: $Fasta -> $OutDir ==" -ForegroundColor Cyan
    $py = Join-Path $Spired 'run_SPIRED-Stab.py'
    & conda run -n spired_fitness --no-capture-output python $py --fasta_file $Fasta --saved_folder $OutDir
    if ($LASTEXITCODE -ne 0) { throw "SPIRED-Stab failed (exit $LASTEXITCODE)" }
}

Invoke-SpiredFitness -Fasta $fitnessIn -OutDir $fitnessOut
Invoke-Gdfold2Pair -Fasta $fitnessIn -OutDir $fitnessOut

foreach ($tag in @("S662F", "P719L", "T750I")) {
    $pair = Join-Path $In "WT_vs_$tag.fasta"
    $stabOut = Join-Path $Here "stability_WT_vs_$tag"
    New-Item -ItemType Directory -Force -Path $stabOut | Out-Null
    Invoke-SpiredStab -Fasta $pair -OutDir $stabOut
    Invoke-Gdfold2Pair -Fasta $pair -OutDir $stabOut
}

Write-Host "== stability_summary.csv ==" -ForegroundColor Cyan
$collector = Join-Path $Here 'collect_stability_summary.py'
& python $collector
if ($LASTEXITCODE -ne 0) { throw "collect_stability_summary failed" }

Write-Host 'Done. Outputs: fitness\, stability_WT_vs_*\, stability_summary.csv' -ForegroundColor Green
