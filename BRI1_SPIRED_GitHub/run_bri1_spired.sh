#!/usr/bin/env bash
# BRI1 550–800 aa：SPIRED-Fitness（一次跑 WT+3 突变）+ SPIRED-Stab（WT vs 各突变体分别跑，各自 pred.csv）
# 需在已配置 conda 环境 spired_fitness / gdfold2 的 Linux 或 WSL 中执行；仓库根目录与 SPIRED-Fitness 并列。
# 纯 Windows（无 WSL）：请用同目录下的 run_bri1_spired.ps1（PowerShell）。
# 若无法安装 GDFold2：run_bri1_stab_only.ps1 仅跑 SPIRED-Stab + stability_summary.csv。
set -Eeuo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${HERE}/.." && pwd)"
SPIRED="${ROOT}/SPIRED-Fitness"
IN="${HERE}/input"

if [[ ! -d "${SPIRED}" ]]; then
  echo "未找到 SPIRED-Fitness: ${SPIRED}" >&2
  exit 1
fi

if [[ ! -f "${IN}/bri1_550-800_fitness.fasta" ]]; then
  echo "请先运行: python prepare_bri1_inputs.py" >&2
  exit 1
fi

mkdir -p "${HERE}/fitness"
mkdir -p "${HERE}/stability_WT_vs_S662F"
mkdir -p "${HERE}/stability_WT_vs_P719L"
mkdir -p "${HERE}/stability_WT_vs_T750I"

echo "== SPIRED-Fitness (WT + S662F + P719L + T750I) =="
bash "${SPIRED}/run_spired_fitness.sh" -i "${IN}/bri1_550-800_fitness.fasta" -o "${HERE}/fitness"

echo "== SPIRED-Stab: WT vs S662F =="
bash "${SPIRED}/run_spired_stab.sh" -i "${IN}/WT_vs_S662F.fasta" -o "${HERE}/stability_WT_vs_S662F"

echo "== SPIRED-Stab: WT vs P719L =="
bash "${SPIRED}/run_spired_stab.sh" -i "${IN}/WT_vs_P719L.fasta" -o "${HERE}/stability_WT_vs_P719L"

echo "== SPIRED-Stab: WT vs T750I =="
bash "${SPIRED}/run_spired_stab.sh" -i "${IN}/WT_vs_T750I.fasta" -o "${HERE}/stability_WT_vs_T750I"

echo "== 汇总 ddG/dTm =="
python "${HERE}/collect_stability_summary.py"

echo "完成。稳定性各对比单独目录: stability_WT_vs_*; 汇总表: stability_summary.csv"
