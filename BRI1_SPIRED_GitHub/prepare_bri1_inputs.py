"""
从本仓库 reference/bri1_550-800.fasta 生成 input/ 下的规范 FASTA：
- bri1_550-800_fitness.fasta：4 条序列，供 SPIRED-Fitness
- WT_vs_<mut>.fasta：WT + 单突变体，供 SPIRED-Stab
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "reference" / "bri1_550-800.fasta"
OUT_DIR = ROOT / "input"

SHORT_IDS = [
    "BRI1_WT_550-800",
    "BRI1_S662F_550-800",
    "BRI1_P719L_550-800",
    "BRI1_T750I_550-800",
]


def parse_fasta(path: Path) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8")
    records: list[tuple[str, str]] = []
    header: str | None = None
    chunks: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header is not None:
                records.append((header, "".join(chunks)))
            header = line[1:].strip()
            chunks = []
        else:
            chunks.append(line)
    if header is not None:
        records.append((header, "".join(chunks)))
    return records


def write_fasta(path: Path, items: list[tuple[str, str]]) -> None:
    lines: list[str] = []
    for seq_id, seq in items:
        lines.append(f">{seq_id}")
        lines.append(seq)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not SRC.is_file():
        raise FileNotFoundError(f"Missing: {SRC}")

    raw = parse_fasta(SRC)
    if len(raw) != 4:
        raise ValueError(f"Expected 4 sequences, got {len(raw)}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    renamed = list(zip(SHORT_IDS, [r[1] for r in raw]))

    fitness_path = OUT_DIR / "bri1_550-800_fitness.fasta"
    write_fasta(fitness_path, renamed)
    print(f"Wrote: {fitness_path}")

    wt_seq = renamed[0][1]
    pairs = [
        ("S662F", renamed[1][1]),
        ("P719L", renamed[2][1]),
        ("T750I", renamed[3][1]),
    ]
    for tag, mut_seq in pairs:
        p = OUT_DIR / f"WT_vs_{tag}.fasta"
        write_fasta(p, [("WT", wt_seq), (f"MUT_{tag}", mut_seq)])
        print(f"Wrote: {p}")


if __name__ == "__main__":
    main()
