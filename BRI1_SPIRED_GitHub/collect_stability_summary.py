"""汇总各 stability_WT_vs_* 目录下的 pred.csv，一行一个对比，不合并计算。"""
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> None:
    rows: list[dict[str, str | float]] = []
    for name in ("S662F", "P719L", "T750I"):
        sub = HERE / f"stability_WT_vs_{name}"
        pred = sub / "pred.csv"
        if not pred.is_file():
            raise FileNotFoundError(f"缺少 {pred}，请先运行 SPIRED-Stab")
        with pred.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            row = next(reader)
        rows.append(
            {
                "comparison": f"WT_vs_{name}",
                "ddG_kcal_mol": float(row["ddG"]),
                "dTm_C": float(row["dTm"]),
                "pred_csv": str(pred.as_posix()),
            }
        )
    out = HERE / "stability_summary.csv"
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["comparison", "ddG_kcal_mol", "dTm_C", "pred_csv"])
        w.writeheader()
        w.writerows(rows)
    print(f"已写入: {out}")


if __name__ == "__main__":
    main()
