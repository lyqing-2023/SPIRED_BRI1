"""
从 bri1_results 下已有 SPIRED-Fitness / SPIRED-Stab 输出生成汇总表与配图。
依赖: pandas, matplotlib, numpy（可用 conda env spired_fitness）
"""
from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
FITNESS = HERE / "fitness"
FIG = HERE / "figures"
TAB = HERE / "tables"

VARIANTS = [
    ("BRI1_WT_550-800", "WT"),
    ("BRI1_S662F_550-800", "S662F"),
    ("BRI1_P719L_550-800", "P719L"),
    ("BRI1_T750I_550-800", "T750I"),
]

MUT_RE = re.compile(r"^([A-Z])(\d+)([A-Z])$")


def _pad_ylim_for_bar_labels(ax, values: np.ndarray, *, label_offset: float, frac: float = 0.22) -> None:
    """扩展 y 轴上下边距，使柱顶/柱底附近的数值标注留在坐标轴边框内。"""
    v = np.asarray(values, dtype=float)
    vmin, vmax = float(v.min()), float(v.max())
    lo = min(0.0, vmin)
    hi = max(0.0, vmax)
    span = max(hi - lo, 1e-9)
    pad = max(label_offset * 6, span * frac)
    ax.set_ylim(lo - pad, hi + pad)


def _setup_font() -> None:
    plt.rcParams["font.sans-serif"] = [
        "Microsoft YaHei",
        "SimHei",
        "Arial Unicode MS",
        "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False


def parse_single_mut_pred(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, index_col=0)
    df.index = df.index.astype(str).str.strip()
    rows = []
    for lab in df.index:
        m = MUT_RE.match(lab)
        if not m:
            continue
        pos = int(m.group(2))
        rows.append({"pos": pos, "pred_score": float(df.loc[lab, "pred_score"])})
    return pd.DataFrame(rows)


def fitness_summary() -> pd.DataFrame:
    out = []
    for folder, short in VARIANTS:
        sm = FITNESS / folder / "single_mut_pred.csv"
        if not sm.is_file():
            raise FileNotFoundError(sm)
        df = parse_single_mut_pred(sm)
        out.append(
            {
                "variant_id": folder,
                "label": short,
                "mean_single_mut_fitness": df["pred_score"].mean(),
                "std_single_mut_fitness": df["pred_score"].std(),
                "n_substitutions": len(df),
            }
        )
    return pd.DataFrame(out)


def plot_stability_bars(stab_csv: Path, out_png: Path) -> None:
    df = pd.read_csv(stab_csv)
    muts = [r.replace("WT_vs_", "") for r in df["comparison"]]
    ddG = df["ddG_kcal_mol"].values
    dTm = df["dTm_C"].values

    fig, (ax0, ax1) = plt.subplots(2, 1, figsize=(8, 7), sharex=True)

    x = np.arange(len(muts))
    w = 0.55
    c_ddG = ["#2E86AB" if v < 0 else "#E94F37" for v in ddG]
    ax0.bar(x, ddG, width=w, color=c_ddG, edgecolor="black", linewidth=0.8)
    ax0.axhline(0, color="black", linewidth=0.9)
    ax0.set_ylabel("ddG (kcal/mol)")
    ax0.set_title("SPIRED-Stab：WT vs 突变体（550–800 片段）\nΔΔG：负值倾向更稳定（模型预测）")
    for i, v in enumerate(ddG):
        ax0.text(i, v + (0.02 if v >= 0 else -0.02), f"{v:.3f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=10)
    _pad_ylim_for_bar_labels(ax0, ddG, label_offset=0.02)

    c_Tm = ["#2E86AB" if v < 0 else "#E94F37" for v in dTm]
    ax1.bar(x, dTm, width=w, color=c_Tm, edgecolor="black", linewidth=0.8)
    ax1.axhline(0, color="black", linewidth=0.9)
    ax1.set_ylabel("dTm (°C)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(muts)
    ax1.set_xlabel("突变")
    ax1.set_title("ΔTm：正值表示模型预测 Tm 升高")
    for i, v in enumerate(dTm):
        ax1.text(i, v + (0.05 if v >= 0 else -0.05), f"{v:.3f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=10)
    _pad_ylim_for_bar_labels(ax1, dTm, label_offset=0.05)

    fig.suptitle("BRI1 区段稳定性：各突变单独对比", fontsize=12, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_fitness_mean_bar(fs: pd.DataFrame, out_png: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    labels = fs["label"].tolist()
    y = fs["mean_single_mut_fitness"].values
    err = fs["std_single_mut_fitness"].values
    x = np.arange(len(labels))
    ax.bar(x, y, yerr=err, capsize=4, color="#44AF69", edgecolor="black", linewidth=0.8, alpha=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("平均 single-mut fitness 分数")
    ax.set_title("SPIRED-Fitness：各序列单点突变预测均值（550–800）")
    for i, v in enumerate(y):
        ax.text(i, v + err[i] + 0.02, f"{v:.3f}", ha="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_fitness_by_position(out_png: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 5))
    cmap = {"WT": "#333333", "S662F": "#E94F37", "P719L": "#2E86AB", "T750I": "#9B59B6"}
    for folder, short in VARIANTS:
        sm = FITNESS / folder / "single_mut_pred.csv"
        df = parse_single_mut_pred(sm)
        g = df.groupby("pos")["pred_score"].mean().sort_index()
        ax.plot(g.index, g.values, label=short, linewidth=1.2, color=cmap.get(short, None))

    ax.set_xlabel("片段内位点索引（与 single_mut_pred 一致）")
    ax.set_ylabel("该位点 20 种替换分数的均值")
    ax.set_title("单点突变 landscape（按位点平均，便于比较 WT 与突变体背景）")
    ax.legend(ncol=4, loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_heatmaps(out_dir: Path) -> None:
    for folder, short in VARIANTS:
        csv_path = FITNESS / folder / "single_mut_pred_for_heatmap.csv"
        df = pd.read_csv(csv_path, index_col=0)
        fig, ax = plt.subplots(figsize=(14, 10))
        im = ax.imshow(df.values, cmap="RdYlGn", aspect="auto", vmin=df.values.min(), vmax=df.values.max())
        plt.colorbar(im, ax=ax, fraction=0.02, label="Fitness score")
        ax.set_xlabel("替换为氨基酸（列）")
        ax.set_ylabel("位点（行，片段内顺序）")
        ax.set_xticks(range(len(df.columns)))
        ax.set_xticklabels(list(df.columns))
        step = max(1, len(df.index) // 25)
        ax.set_yticks(range(0, len(df.index), step))
        ax.set_yticklabels([df.index[i] for i in range(0, len(df.index), step)])
        ax.set_title(f"SPIRED-Fitness 热图 — {short} (BRI1 550–800)")
        fig.tight_layout()
        fig.savefig(out_dir / f"heatmap_{short}.png", dpi=300, bbox_inches="tight")
        plt.close(fig)


def build_combined_table(fs: pd.DataFrame, stab_csv: Path) -> pd.DataFrame:
    stab = pd.read_csv(stab_csv)
    stab = stab.rename(
        columns={
            "comparison": "stab_comparison",
            "ddG_kcal_mol": "ddG_kcal_mol",
            "dTm_C": "dTm_C",
        }
    )
    rows = []
    for _, r in fs.iterrows():
        label = r["label"]
        row = {
            "label": label,
            "mean_single_mut_fitness": r["mean_single_mut_fitness"],
            "std_single_mut_fitness": r["std_single_mut_fitness"],
            "ddG_kcal_mol": np.nan,
            "dTm_C": np.nan,
            "stab_note": "",
        }
        if label == "WT":
            row["stab_note"] = "Stab 为 WT vs 突变体；WT 本身无 ddG/dTm"
        else:
            key = f"WT_vs_{label}"
            m = stab[stab["stab_comparison"] == key]
            if len(m):
                row["ddG_kcal_mol"] = m["ddG_kcal_mol"].values[0]
                row["dTm_C"] = m["dTm_C"].values[0]
                row["stab_note"] = key
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    _setup_font()
    FIG.mkdir(parents=True, exist_ok=True)
    TAB.mkdir(parents=True, exist_ok=True)

    fs = fitness_summary()
    fs.to_csv(TAB / "fitness_summary_by_variant.csv", index=False, encoding="utf-8-sig")

    stab_path = HERE / "stability_summary.csv"
    if stab_path.is_file():
        plot_stability_bars(stab_path, FIG / "stability_ddG_dTm_by_mutant.png")
        combined = build_combined_table(fs, stab_path)
        combined.to_csv(TAB / "presentation_summary.csv", index=False, encoding="utf-8-sig")
    else:
        combined = fs.copy()
        combined.to_csv(TAB / "presentation_summary.csv", index=False, encoding="utf-8-sig")

    plot_fitness_mean_bar(fs, FIG / "fitness_mean_by_variant.png")
    plot_fitness_by_position(FIG / "fitness_position_mean_landscape.png")
    plot_heatmaps(FIG)

    print("Written:")
    for p in sorted(FIG.glob("*.png")):
        print(f"  {p}")
    for p in sorted(TAB.glob("*.csv")):
        print(f"  {p}")


if __name__ == "__main__":
    main()
