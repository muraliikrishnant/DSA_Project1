from __future__ import annotations

import argparse
import csv
import os
from dataclasses import dataclass
from datetime import datetime

from bloom_filter import BloomFilter


@dataclass(frozen=True)
class SweepRow:
    m_bits: int
    k_hashes: int
    n_items: int
    trials: int
    empirical_fpr: float
    theoretical_fpr: float


def measure_fpr(*, m_bits: int, k_hashes: int, n_items: int, trials: int, seed: int) -> SweepRow:
    bf = BloomFilter(m_bits=m_bits, k_hashes=k_hashes)
    added = [f"ip-{i}" for i in range(n_items)]
    for s in added:
        bf.add(s)

    false_pos = 0
    for i in range(trials):
        q = f"q-{seed}-{i}"
        if q in bf:
            false_pos += 1

    empirical = false_pos / trials if trials else 0.0
    theoretical = BloomFilter.theoretical_fpr(m_bits, k_hashes, n_items)
    return SweepRow(
        m_bits=m_bits,
        k_hashes=k_hashes,
        n_items=n_items,
        trials=trials,
        empirical_fpr=empirical,
        theoretical_fpr=theoretical,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Run a Bloom filter false-positive-rate sweep and write CSV.")
    ap.add_argument("--m-bits", dest="m_bits", nargs="+", type=int, required=True, help="List of m values (bits)")
    ap.add_argument("--k-hashes", dest="k_hashes", type=int, default=7)
    ap.add_argument("--n-items", dest="n_items", type=int, default=50_000)
    ap.add_argument("--trials", type=int, default=100_000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=str, default=None, help="CSV output path (default: submission_artifacts/bloom_fpr_sweep_*.csv)")
    args = ap.parse_args()

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = args.out or os.path.join("submission_artifacts", f"bloom_fpr_sweep_{now}.csv")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    rows: list[SweepRow] = []
    for m in args.m_bits:
        rows.append(
            measure_fpr(
                m_bits=m,
                k_hashes=args.k_hashes,
                n_items=args.n_items,
                trials=args.trials,
                seed=args.seed,
            )
        )

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "m_bits",
                "k_hashes",
                "n_items",
                "trials",
                "empirical_fpr",
                "theoretical_fpr",
            ],
        )
        w.writeheader()
        for r in rows:
            w.writerow(
                {
                    "m_bits": r.m_bits,
                    "k_hashes": r.k_hashes,
                    "n_items": r.n_items,
                    "trials": r.trials,
                    "empirical_fpr": f"{r.empirical_fpr:.8f}",
                    "theoretical_fpr": f"{r.theoretical_fpr:.8f}",
                }
            )

    meta_path = out_path.replace(".csv", "_meta.txt")
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write(f"timestamp={datetime.now().isoformat()}\n")
        f.write(f"m_bits={args.m_bits}\n")
        f.write(f"k_hashes={args.k_hashes}\n")
        f.write(f"n_items={args.n_items}\n")
        f.write(f"trials={args.trials}\n")
        f.write(f"seed={args.seed}\n")

    print(f"Wrote: {out_path}")
    print(f"Wrote: {meta_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

