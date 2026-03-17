# DSA Project 1 — Fast Intrusion Detection (Spring 2026)

This repo contains from-scratch implementations used in the pre-proposal:

- Hash-table counting (`hash_counter.py`) — **O(n)**
- Randomized Quick Sort (`quicksort.py`) — **O(n log n)** average
- Merge Sort (`mergesort.py`) — **O(n log n)** worst-case
- Heap Top-K (`heap_topk.py`) — **O(n log K)**
- Bloom filter (`bloom_filter.py`) — **O(1)** membership (probabilistic)
- Dataset loader for CICIDS/KDD99 (`dataset_loader.py`)
- Benchmark harness (`benchmark.py`)

## Run benchmarks

Benchmark counting + ranking algorithms (writes a CSV under `results/`).

```bash
python3 benchmark.py algos --dataset cicids --dataset-path CICIDS --limits 10000 100000 --cicids-column "Destination Port" --runs 3 --verify
```

KDD99 (default key field: `service`):

```bash
python3 benchmark.py algos --dataset kdd99 --dataset-path KDD99/kddcup.data.corrected --limits 10000 100000 --kdd99-field service --runs 3 --verify
```

Enable the **O(n²)** brute-force baseline (only runs when `n <= --bruteforce-max-n`):

```bash
python3 benchmark.py algos --dataset kdd99 --dataset-path KDD99/kddcup.data_10_percent/kddcup.data_10_percent --limits 2000 5000 10000 --do-bruteforce --verify
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

- The CICIDS CSVs in this folder appear to omit IP columns; benchmark by choosing a different key column (default: `Destination Port`).
- The benchmark defaults to `--runs 3` for practicality; the proposal specifies **10**.
