# BRI1 (550–800 aa) · SPIRED-Fitness & SPIRED-Stab case

本地可复现的 **BRI1 野生型与三个点突变体**（S662F、P719L、T750I）在 **氨基酸 550–800 区段**上的计算分析：输入序列、脚本、**汇总表与配图**（本仓库已包含一次完整运行的 CSV/PNG 结果）。

**论文**：SPIRED-Fitness — [Nature Communications 2024](https://doi.org/10.1038/s41467-024-51776-x)。模型权重与上游代码见 [Gonglab-THU/SPIRED-Fitness](https://github.com/Gonglab-THU/SPIRED-Fitness)。

## 仓库里有什么

| 路径 | 说明 |
|------|------|
| `reference/bri1_550-800.fasta` | 区段 WT + 3 突变体原始序列（与 `prepare_bri1_inputs.py` 配套） |
| `input/` | 已生成的 SPIRED 输入 FASTA（可删后由脚本重建） |
| `fitness/**.csv` | SPIRED-Fitness 输出的 **表格部分**（单点/双点/热图矩阵）；**不含** PDB、npz、pt，以控制仓库体积 |
| `figures/*.png` | 由 `generate_bri1_figures.py` 生成的解读用图 |
| `tables/*.csv` | 按 variant 与汇报整理的汇总表 |
| `stability_summary.csv` + `stability_WT_vs_*/pred.csv` | SPIRED-Stab 的 **ddG/dTm**（每个突变单独对比 WT） |
| `generate_bri1_figures.py` | 从 `fitness/` CSV 与 `stability_summary.csv` 重画图与表 |
| `run_bri1_stab_only.ps1` 等 | 在已安装 [SPIRED-Fitness](https://github.com/Gonglab-THU/SPIRED-Fitness) 与 `conda` 环境的前提下调用推理（见该仓库 README） |

## 复现作图（无需重跑大模型）

```bash
python generate_bri1_figures.py
```

依赖：`pandas`、`matplotlib`、`numpy`。

## 布局说明（与完整工作目录的区别）

将 **SPIRED-Fitness** 仓库克隆到与本仓库**同级目录**，例如：

```text
your_workspace/
  SPIRED-Fitness/     # git clone Gonglab-THU/SPIRED-Fitness
  BRI1_SPIRED_GitHub/ # 本仓库
```

则 `run_bri1_stab_only.ps1` / `run_bri1_spired.ps1` 中的路径可找到 `../SPIRED-Fitness`。

## 免责声明

结果为 **深度学习模型预测**，不替代实验；区段截断与全长蛋白行为可能不一致。公开本仓库旨在展示流程与可复现材料，**不构成**临床或育种建议。
