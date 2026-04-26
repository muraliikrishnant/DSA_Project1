# DSA Project 1: Fast Intrusion Detection (Spring 2026) - Project Overview

## Goal
The primary objective of this project is to implement and benchmark various Data Structures and Algorithms (DSA) for processing network security logs. The project focuses on "Heavy Hitter" detection (finding the most frequent IP addresses or ports in a stream of network traffic) and efficient membership testing using Bloom Filters.

## Core Components
The project is divided into several functional areas:

1.  **Frequency Counting**: Counting how many times each unique key (e.g., IP address, port) appears in a dataset.
2.  **Sorting & Ranking**: Ordering the unique keys by their frequency to identify the top offenders (Heavy Hiters).
3.  **Top-K Selection**: Efficiently finding only the top *K* most frequent items without sorting the entire list.
4.  **Membership Testing**: Using probabilistic data structures (Bloom Filters) to quickly check if a key has been seen before.
5.  **Data Loading & Generation**: Loading real-world datasets (CICIDS, KDD99) or generating synthetic data with specific distributions (Uniform, Zipf, and explicit 5%->80% hotspot skew).
6.  **Benchmarking & Visualization**: A harness to measure the performance (time and memory) of these algorithms and scripts to plot the results.

## Algorithms Implemented
- **Hash Table Counting**: O(n) time complexity for frequency counting.
- **Randomized Quick Sort**: O(n log n) average time for sorting by frequency.
- **Bottom-up Merge Sort**: O(n log n) guaranteed time for stable sorting.
- **Heap-based Top-K**: O(n log K) time to find the top K items.
- **Bloom Filter**: O(1) time for insertions and lookups (probabilistic).
- **Brute-force Counting**: O(n^2) intentional baseline for performance comparison.

## Project Structure
- `About/`: Contains detailed documentation for each component (this directory).
- `CICIDS/`, `KDD99/`: Directories for real-world network datasets.
- `results/`: Output directory for benchmark CSV files.
- `tests/`: Unit tests for ensuring algorithm correctness.
- `benchmark.py`: The main entry point for running experiments.
- `plot_results.py`: Script to generate charts from benchmark data.

## Proposal-Alignment Notes
- The official reproducibility artifacts use **10 runs per experiment** (`submission_artifacts/*_10runs*`).
- For CICIDS, the benchmark key is `Destination Port` because the provided CSVs do not expose stable IP columns.
- The synthetic attack simulation can be run in explicit 5%-hot/80%-traffic mode via `--synthetic-mode hotspot --hot-fraction 0.05 --hot-traffic-share 0.8`.
