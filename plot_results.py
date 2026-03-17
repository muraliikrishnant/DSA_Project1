from __future__ import annotations

import argparse
import csv
import math
import os
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Row:
    n: int
    distribution: str
    algo: str
    seconds_mean: float
    seconds_std: float
    peak_kb_mean: float
    peak_kb_std: float
    unique_keys: int


def _read_csv(path: str) -> list[Row]:
    rows: list[Row] = []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for d in r:
            rows.append(
                Row(
                    n=int(d["n"]),
                    distribution=str(d.get("distribution", "")),
                    algo=str(d.get("algo", "")),
                    seconds_mean=float(d.get("seconds_mean", 0.0)),
                    seconds_std=float(d.get("seconds_std", 0.0)),
                    peak_kb_mean=float(d.get("peak_kb_mean", 0.0)),
                    peak_kb_std=float(d.get("peak_kb_std", 0.0)),
                    unique_keys=int(d.get("unique_ips") or 0),
                )
            )
    return rows


def _theory_funcs(k: int) -> dict[str, callable]:
    return {
        "O(n)": lambda n: n,
        "O(n log n)": lambda n: n * math.log(max(n, 2)),
        f"O(n log {k})": lambda n: n * math.log(max(k, 2)),
        "O(n^2)": lambda n: n * n,
    }


def _scale_line(xs: list[int], ys: list[float], f) -> list[float]:
    if not xs or not ys:
        return []
    x0, y0 = xs[0], ys[0]
    denom = float(f(x0)) or 1.0
    c = y0 / denom
    return [c * float(f(x)) for x in xs]


def _plot(
    *,
    series: dict[tuple[str, str], list[Row]],
    x_field: str,
    y_field: str,
    yerr_field: str,
    out_path: Path,
    loglog: bool,
    k: int,
) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt
    except Exception as e:  # pragma: no cover
        raise RuntimeError("matplotlib is required for plotting. Try: python3 -m pip install matplotlib") from e

    plt.figure(figsize=(10, 6))

    # Plot each curve
    for (dist, algo), rows in sorted(series.items()):
        rows = sorted(rows, key=lambda r: getattr(r, x_field))
        xs = [getattr(r, x_field) for r in rows]
        ys = [getattr(r, y_field) for r in rows]
        yerr = [getattr(r, yerr_field) for r in rows]
        label = f"{dist}:{algo}"
        plt.errorbar(xs, ys, yerr=yerr, marker="o", linewidth=2, capsize=3, label=label)

    # Overlay theoretical reference lines (scaled to the first available curve of each class when present).
    theory = _theory_funcs(k)
    by_algo: dict[str, list[Row]] = defaultdict(list)
    for (_dist, algo), rows in series.items():
        by_algo[algo].extend(rows)

    def overlay(name: str, f, anchor_algo: str) -> None:
        if anchor_algo not in by_algo:
            return
        anchor = sorted(by_algo[anchor_algo], key=lambda r: getattr(r, x_field))
        xs = [getattr(r, x_field) for r in anchor]
        ys = [getattr(r, y_field) for r in anchor]
        line = _scale_line(xs, ys, f)
        if line:
            plt.plot(xs, line, linestyle="--", linewidth=1.5, label=name, alpha=0.8)

    overlay("O(n) reference", theory["O(n)"], anchor_algo="count_hash")
    overlay("O(n log n) reference", theory["O(n log n)"], anchor_algo="mergesort")
    overlay(f"O(n log {k}) reference", theory[f"O(n log {k})"], anchor_algo="topk_heap")
    overlay("O(n^2) reference", theory["O(n^2)"], anchor_algo="bruteforce")

    plt.title(out_path.stem.replace("_", " ").title())
    x_labels = {"n": "Number of Log Entries (n)", "unique_keys": "Number of Unique Keys"}
    y_labels = {"seconds_mean": "Runtime (seconds)", "peak_kb_mean": "Peak Memory (KB)"}
    plt.xlabel(x_labels.get(x_field, x_field))
    plt.ylabel(y_labels.get(y_field, y_field))
    plt.grid(True, which="both", linestyle=":", linewidth=0.8)
    if loglog:
        plt.xscale("log")
        plt.yscale("log")
    plt.legend(fontsize=8)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


def main() -> int:
    ap = argparse.ArgumentParser(description="Plot benchmark CSV results into charts.")
    ap.add_argument("--csv", required=True, help="Path to benchmark_*.csv produced by benchmark.py")
    ap.add_argument("--outdir", default="plots", help="Output directory for PNGs")
    ap.add_argument("--x", choices=["n", "unique_keys"], default="n", help="X-axis field")
    ap.add_argument("--k", type=int, default=10, help="K used for the O(n log K) reference line label")
    ap.add_argument("--distribution", default=None, help="Filter to a single distribution (e.g. cicids or kdd99)")
    args = ap.parse_args()

    # Matplotlib/fontconfig cache dirs are sometimes non-writable in sandboxed environments.
    cache_root = Path(tempfile.gettempdir()) / "dsa_project1_plot_cache"
    mpl_dir = cache_root / "matplotlib"
    xdg_dir = cache_root / "xdg"
    mpl_dir.mkdir(parents=True, exist_ok=True)
    xdg_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_dir))
    os.environ.setdefault("XDG_CACHE_HOME", str(xdg_dir))

    rows = _read_csv(args.csv)
    if args.distribution:
        rows = [r for r in rows if r.distribution == args.distribution]
    if not rows:
        print("No rows to plot.")
        return 2

    series: dict[tuple[str, str], list[Row]] = defaultdict(list)
    for r in rows:
        series[(r.distribution, r.algo)].append(r)

    outdir = Path(args.outdir)
    x_field = args.x

    _plot(
        series=series,
        x_field=x_field,
        y_field="seconds_mean",
        yerr_field="seconds_std",
        out_path=outdir / "runtime_vs_x.png",
        loglog=False,
        k=args.k,
    )
    _plot(
        series=series,
        x_field=x_field,
        y_field="seconds_mean",
        yerr_field="seconds_std",
        out_path=outdir / "runtime_vs_x_loglog.png",
        loglog=True,
        k=args.k,
    )
    _plot(
        series=series,
        x_field=x_field,
        y_field="peak_kb_mean",
        yerr_field="peak_kb_std",
        out_path=outdir / "memory_vs_x.png",
        loglog=False,
        k=args.k,
    )
    _plot(
        series=series,
        x_field=x_field,
        y_field="peak_kb_mean",
        yerr_field="peak_kb_std",
        out_path=outdir / "memory_vs_x_loglog.png",
        loglog=True,
        k=args.k,
    )

    print(f"Wrote plots to: {outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
