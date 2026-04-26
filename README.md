# DSA Project 1 — Fast Intrusion Detection (Spring 2026)

This repo contains from-scratch implementations used in the pre-proposal:

- Hash-table counting (`hash_counter.py`) — **O(n)**
- Randomized Quick Sort (`quicksort.py`) — **O(n log n)** average
- Merge Sort (`mergesort.py`) — **O(n log n)** worst-case
- Heap Top-K (`heap_topk.py`) — **O(n log K)**
- Bloom filter (`bloom_filter.py`) — **O(1)** membership (probabilistic)
- Dataset loader for CICIDS/KDD99 (`dataset_loader.py`)
- Synthetic key generator (`data_generator.py`)
- Benchmark harness (`benchmark.py`)

## Run benchmarks (proposal-aligned defaults)

Benchmark counting + ranking algorithms (writes a CSV under `results/`).

```bash
python3 benchmark.py algos --dataset cicids --dataset-path CICIDS --limits 10000 100000 --cicids-column "Destination Port" --runs 10 --verify
```

KDD99 (default key field: `service`):

```bash
python3 benchmark.py algos --dataset kdd99 --dataset-path KDD99/kddcup.data.corrected --limits 10000 100000 --kdd99-field label --runs 10 --verify
```

Enable the **O(n²)** brute-force baseline (only runs when `n <= --bruteforce-max-n`):

```bash
python3 benchmark.py algos --dataset synthetic --limits 1000 2000 5000 10000 --synthetic-mode hotspot --synthetic-unique 1000 --hot-fraction 0.05 --hot-traffic-share 0.8 --do-bruteforce --runs 10 --verify
```

Synthetic at n ∈ {10⁴, 10⁵, 10⁶, 10⁷}:

```bash
python3 benchmark.py algos --dataset synthetic --limits 10000 100000 1000000 10000000 --synthetic-mode hotspot --synthetic-unique 1000 --synthetic-unique-scale --hot-fraction 0.05 --hot-traffic-share 0.8 --runs 10 --verify
```

## Bloom filter experiment

```bash
python3 benchmark.py bloom --m-bits 1000000 --k-hashes 7 --n-items 50000 --trials 100000
```

## Plot results

`benchmark.py` writes CSV files under `results/`. Convert a CSV into the four required charts (runtime/memory on linear + log-log axes):

```bash
python3 plot_results.py --csv results/benchmark_YYYYMMDD_HHMMSS.csv
```

## Run tests

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Notes / Limitations

- **Official submission artifacts are `*_10runs*` only.**
- The benchmark default is now `--runs 10` to match proposal methodology.
- CICIDS files in this repo do not include stable source/destination IP fields, so the CICIDS benchmark key is `Destination Port`. This is intentional and documented in metadata.
- Synthetic skew supports:
  - `--synthetic-mode hotspot` for explicit **5% of keys -> 80% of traffic**.
  - `--synthetic-mode zipf` for heavy-tailed Zipf-like skew (supplementary).
- Proposal text mentions Python 3.11; experiments were executed in a compatible Python 3.12 environment and each run records exact interpreter version in `*_meta.txt`.
