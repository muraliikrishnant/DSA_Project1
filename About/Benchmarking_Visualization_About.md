# About: Benchmarking and Visualization

This documentation covers the tools used to measure algorithm performance and generate charts.

## 1. Benchmark Harness (`benchmark.py`)
- **What it is**: The central command-line tool for running all experiments.
- **How it's written**:
    - Uses `argparse` for a sub-command-based CLI (`algos` and `bloom`).
    - `_measure`: A wrapper function that uses `time.perf_counter()` for precision and `tracemalloc` to track peak memory usage.
    - `bench_algorithms`: Orchestrates the testing of counting, sorting, and Top-K algorithms across multiple runs and data sizes.
    - Synthetic modes include `uniform`, `zipf`, and `hotspot` (explicit 5%-hot/80%-traffic profile for proposal alignment).
    - `bench_bloom`: Measures the empirical False Positive Rate (FPR) of the Bloom Filter by inserting *n* items and testing for membership of *trials* non-existent items.
- **Key Functions**:
    - `main()`: Entry point that parses arguments and dispatches to sub-benchmarks.
    - `emit()`: Aggregates timing and memory statistics (mean, std dev) for each algorithm and appends them to a result list.
- **Result**: A CSV file in the `results/` folder and a `_meta.txt` file containing system environment details (including exact Python version used for that run).

## 2. Result Plotting (`plot_results.py`)
- **What it is**: A script to turn benchmark CSVs into visualizations.
- **How it's written**:
    - Uses `matplotlib` to generate PNG images.
    - Implements automated scaling of theoretical reference lines (O(n), O(n log n), O(n^2)). These lines are anchored to the first data point of a corresponding algorithm to provide a clear baseline for comparison.
    - Supports log-log plotting, which is essential for visualizing complexity across several orders of magnitude.
- **Key Function**: `_plot(...)`: Generates four types of charts: Runtime/Memory on both Linear and Log-Log axes.
- **Result**: PNG files in the `plots/` directory.

## 3. Bloom Sweep (`bloom_sweep.py`)
- **What it is**: A specialized script to explore how different Bloom Filter parameters (m, k, n) affect its False Positive Rate.
- **How it's written**:
    - Runs a "sweep" over ranges of parameters (e.g., varying the number of bits *m* while keeping *n* constant).
    - Compares empirical FPR (observed during testing) with the theoretical FPR (from the formula).
- **Result**: Typically used to generate data for "Heatmaps" or "Sweep Charts" showing the trade-off between memory and accuracy.

## Summary of Results
The benchmark and plotting tools are designed to demonstrate several key DSA concepts:
1.  **Complexity**: O(n) hash counting is significantly faster than O(n log n) sorting, which is vastly faster than O(n^2) brute-force.
2.  **Scalability**: Linear charts show the growth of O(n) vs. O(n^2), while log-log charts help confirm the *exponent* of growth.
3.  **Memory**: Tracking peak memory helps identify the trade-off between time and space (e.g., sorting in-place vs. creating a new list).
4.  **Accuracy**: The Bloom Filter results show how choosing the optimal *k* for a given *m/n* ratio can minimize false positives.
