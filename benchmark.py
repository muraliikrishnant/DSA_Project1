from __future__ import annotations

import argparse
import csv
import os
import platform
import statistics
import time
import tracemalloc
from dataclasses import dataclass
from datetime import datetime

from bloom_filter import BloomFilter
from bruteforce import rank_bruteforce
from data_generator import generate_uniform_keys, generate_zipf_keys
from dataset_loader import load_keys
from hash_counter import count_frequencies
from heap_topk import top_k
from mergesort import mergesort
from quicksort import quicksort_in_place


@dataclass(frozen=True)
class RunMetric:
    seconds: float
    peak_kb: int


def _measure(fn) -> RunMetric:
    tracemalloc.start()
    t0 = time.perf_counter()
    fn()
    t1 = time.perf_counter()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return RunMetric(seconds=t1 - t0, peak_kb=int(peak // 1024))


def _mean_std(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    if len(values) == 1:
        return values[0], 0.0
    return statistics.mean(values), statistics.stdev(values)


def _write_csv(path: str, rows: list[dict[str, object]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def bench_algorithms(args: argparse.Namespace) -> int:
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = args.out or os.path.join("results", f"benchmark_{now}.csv")

    rows: list[dict[str, object]] = []
    for n in args.limits:
        tag = args.dataset.lower()
        keys: list[str] | None = None
        source: str

        if tag == "synthetic":
            source = f"synthetic:{args.synthetic_mode} unique={args.synthetic_unique} alpha={args.zipf_alpha}"

            def iter_keys(seed: int):
                if args.synthetic_mode == "uniform":
                    return generate_uniform_keys(n, num_ips=args.synthetic_unique, seed=seed)
                return generate_zipf_keys(n, num_ips=args.synthetic_unique, alpha=args.zipf_alpha, seed=seed)

        else:
            loaded = load_keys(
                args.dataset,
                args.dataset_path,
                limit=n,
                cicids_column=args.cicids_column,
                kdd99_field=args.kdd99_field,
            )
            source = loaded.source
            keys = loaded.keys
            iter_keys = None  # type: ignore[assignment]

        if args.verbose:
            if keys is not None:
                print(f"Loaded {len(keys)} rows from {source}")
            else:
                print(f"Configured synthetic generator for n={n}: {source}")

        count_metrics: list[RunMetric] = []
        qsort_metrics: list[RunMetric] = []
        msort_metrics: list[RunMetric] = []
        topk_metrics: list[RunMetric] = []
        brute_metrics: list[RunMetric] = []

        unique_last = None

        for r in range(args.runs):
            counts: dict[object, int] = {}

            def do_count() -> None:
                nonlocal counts
                if keys is not None:
                    counts = count_frequencies(keys)
                else:
                    counts = count_frequencies(iter_keys(args.seed + r))

            count_metrics.append(_measure(do_count))
            unique_last = len(counts)
            items = list(counts.items())

            if args.do_quicksort:
                data = items.copy()

                def do_qsort() -> None:
                    quicksort_in_place(data, seed=args.seed + r)

                qsort_metrics.append(_measure(do_qsort))

            if args.do_mergesort:
                data = items.copy()

                def do_msort() -> None:
                    _ = mergesort(data)

                msort_metrics.append(_measure(do_msort))

            if args.do_topk:
                def do_topk() -> None:
                    _ = top_k(items, args.k)

                topk_metrics.append(_measure(do_topk))

            if args.do_bruteforce and n <= args.bruteforce_max_n:
                if keys is not None:
                    logs = keys
                else:
                    logs = list(iter_keys(args.seed + r))

                def do_brute() -> None:
                    _ = rank_bruteforce(logs)

                brute_metrics.append(_measure(do_brute))

            if args.verify and unique_last and unique_last <= args.verify_max_unique:
                # Correctness baselines (allowed only for verification).
                baseline_sorted = sorted(items, key=lambda t: (-t[1], t[0]))
                if args.do_quicksort:
                    data = items.copy()
                    quicksort_in_place(data, seed=args.seed + r)
                    if data != baseline_sorted:
                        raise AssertionError("Quicksort mismatch vs baseline")
                if args.do_mergesort:
                    data = mergesort(items)
                    if data != baseline_sorted:
                        raise AssertionError("Mergesort mismatch vs baseline")
                if args.do_topk:
                    topk = top_k(items, args.k)
                    if topk != baseline_sorted[: min(args.k, len(baseline_sorted))]:
                        raise AssertionError("Top-K mismatch vs baseline")

        def emit(algo: str, metrics: list[RunMetric]) -> None:
            if not metrics:
                return
            secs = [m.seconds for m in metrics]
            peaks = [m.peak_kb for m in metrics]
            sec_mean, sec_std = _mean_std(secs)
            peak_mean, peak_std = _mean_std([float(p) for p in peaks])
            rows.append(
                {
                    "n": n,
                    "distribution": tag,
                    "dataset_source": source,
                    "unique_ips": unique_last,
                    "algo": algo,
                    "runs": args.runs,
                    "seconds_mean": round(sec_mean, 6),
                    "seconds_std": round(sec_std, 6),
                    "peak_kb_mean": round(peak_mean, 3),
                    "peak_kb_std": round(peak_std, 3),
                    "k": args.k if algo == "topk_heap" else "",
                }
            )

        emit("count_hash", count_metrics)
        emit("quicksort", qsort_metrics)
        emit("mergesort", msort_metrics)
        emit("topk_heap", topk_metrics)
        emit("bruteforce", brute_metrics)

    if not rows:
        print("No rows to write (did you disable all algorithms?)")
        return 2

    # Add a small header row as a separate file for reproducibility.
    _write_csv(out_path, rows)
    meta_path = out_path.replace(".csv", "_meta.txt")
    os.makedirs(os.path.dirname(meta_path), exist_ok=True)
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write(f"python={platform.python_version()}\n")
        f.write(f"platform={platform.platform()}\n")
        f.write(f"cpu={platform.processor()}\n")
        f.write(f"timestamp={datetime.now().isoformat()}\n")
        f.write(f"dataset={args.dataset}\n")
        f.write(f"dataset_path={args.dataset_path}\n")
        f.write(f"cicids_column={args.cicids_column}\n")
        f.write(f"kdd99_field={args.kdd99_field}\n")
        f.write(f"limits={args.limits}\n")
        f.write(f"runs={args.runs}\n")
        f.write(f"k={args.k}\n")

    print(f"Wrote: {out_path}")
    print(f"Wrote: {meta_path}")

    return 0


def bench_bloom(args: argparse.Namespace) -> int:
    rng_seed = args.seed
    n = args.n_items

    bf = BloomFilter(m_bits=args.m_bits, k_hashes=args.k_hashes)
    added = [f"ip-{i}" for i in range(n)]
    for s in added:
        bf.add(s)

    trials = args.trials
    false_pos = 0
    for i in range(trials):
        q = f"q-{rng_seed}-{i}"
        if q in bf:
            false_pos += 1

    empirical = false_pos / trials if trials else 0.0
    theoretical = BloomFilter.theoretical_fpr(args.m_bits, args.k_hashes, n)
    print(f"m_bits={args.m_bits} k={args.k_hashes} n={n} trials={trials}")
    print(f"empirical_fpr={empirical:.6f}")
    print(f"theoretical_fpr={theoretical:.6f}")
    return 0


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="DSA Project 1 benchmarking harness")
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("algos", help="Benchmark counting/sorting/top-k")
    pa.add_argument("--dataset", choices=["cicids", "kdd99", "synthetic"], required=True)
    pa.add_argument(
        "--dataset-path",
        type=str,
        default=None,
        help="For cicids: directory of .csv files. For kdd99: path to data file (supports .gz). Not used for synthetic.",
    )
    pa.add_argument("--limits", nargs="+", type=int, default=[10_000, 100_000, 1_000_000], help="Prefix lengths to load from the dataset")
    pa.add_argument("--sizes", nargs="+", type=int, help="Alias for --limits")
    pa.add_argument("--runs", type=int, default=3, help="Repeats per setting (PDF: 10)")
    pa.add_argument("--seed", type=int, default=0)
    pa.add_argument("--cicids-column", type=str, default="Destination Port", help="Key column for CICIDS CSVs (often no IP columns)")
    pa.add_argument("--kdd99-field", type=str, default="service", help="Key field for KDD99 (e.g. service, protocol_type, flag, label, or numeric index)")
    pa.add_argument("--synthetic-mode", choices=["uniform", "zipf"], default="zipf", help="Synthetic distribution")
    pa.add_argument("--synthetic-unique", type=int, default=1000, help="Number of unique synthetic IPs")
    pa.add_argument("--zipf-alpha", type=float, default=1.2, help="Zipf alpha (higher => more skew)")
    pa.add_argument("-k", type=int, default=10, help="Top-K size")
    pa.add_argument("--no-quicksort", dest="do_quicksort", action="store_false")
    pa.add_argument("--no-mergesort", dest="do_mergesort", action="store_false")
    pa.add_argument("--no-topk", dest="do_topk", action="store_false")
    pa.add_argument("--do-bruteforce", dest="do_bruteforce", action="store_true", help="Enable O(n^2) baseline (small n only)")
    pa.add_argument("--bruteforce-max-n", type=int, default=20_000)
    pa.add_argument("--verify", action="store_true", help="Verify outputs against Python baseline for small unique sizes")
    pa.add_argument("--verify-max-unique", type=int, default=50_000)
    pa.add_argument("--out", type=str, default=None, help="CSV output path (default: results/benchmark_*.csv)")
    pa.add_argument("--verbose", action="store_true")
    pa.set_defaults(func=bench_algorithms)

    pb = sub.add_parser("bloom", help="Measure Bloom filter false positive rate")
    pb.add_argument("--m-bits", dest="m_bits", type=int, default=1_000_000)
    pb.add_argument("--k-hashes", dest="k_hashes", type=int, default=7)
    pb.add_argument("--n-items", dest="n_items", type=int, default=50_000)
    pb.add_argument("--trials", type=int, default=100_000)
    pb.add_argument("--seed", type=int, default=0)
    pb.set_defaults(func=bench_bloom)

    return p.parse_args()


def main() -> int:
    args = parse_args()
    if getattr(args, "sizes", None):
        # Backward-compatible alias
        args.limits = args.sizes
    if args.cmd == "algos":
        if args.dataset != "synthetic" and not args.dataset_path:
            raise SystemExit("--dataset-path is required for cicids/kdd99")
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
