# About: Data Generation, Loading, and Counting

This documentation covers the components used for data preparation and the O(n) frequency counting implementation.

## 1. Data Generation (`data_generator.py`)
- **What it is**: A script to generate synthetic IPv4 address logs for benchmarking.
- **How it's written**:
    - Uses `random.Random` with a seed for deterministic results.
    - `_make_ipv4_pool`: Creates a fixed pool of unique IPv4 addresses.
    - `generate_uniform_keys`: Selects IP addresses uniformly from the pool (every IP has an equal chance of appearing).
    - `generate_zipf_keys`: Selects IP addresses based on a **Zipf distribution**, where a few addresses appear very frequently while most appear rarely. This mimics real-world network traffic.
- **Key Functions**:
    - `generate_uniform_keys(n, num_ips, seed)`: Generates *n* keys with *num_ips* unique ones.
    - `generate_zipf_keys(n, num_ips, alpha, seed)`: Generates skewed keys. Higher *alpha* means more skew.
- **Result**: An iterator that yields IPv4 strings.

## 2. Dataset Loader (`dataset_loader.py`)
- **What it is**: A utility to load network logs from real-world datasets (CICIDS and KDD99).
- **How it's written**:
    - Handles both raw text and `.gz` compressed files.
    - `iter_cicids_keys`: Parses CSV files from a directory, identifying columns by header name (case-insensitive).
    - `iter_kdd99_keys`: Parses comma-separated values where fields are identified by fixed indices.
- **Key Function**: `load_keys(dataset, dataset_path, limit, cicids_column, kdd99_field)`: Loads up to `limit` keys from the specified dataset.
- **Result**: A `LoadedDataset` object containing a list of strings and its source description.

## 3. Hash Table Counting (`hash_counter.py`)
- **What it is**: An O(n) implementation for counting frequencies using Python's built-in dictionary (hash table).
- **How it's written**:
    - Uses a simple loop to iterate through the stream of keys.
    - For each key, it updates its count in a dictionary.
    - Includes helper functions for converting between IPv4 string and integer formats.
- **Key Functions**:
    - `count_frequencies(stream)`: Returns a dictionary of `{key: count}`.
    - `ipv4_str_to_int(ip)`: Converts a dotted IP string to a 32-bit integer for efficient storage or processing.
    - `extract_first_ipv4_int(line)`: Uses regex to find and convert the first IPv4 address in a log line.
- **Complexity**: O(n) time and O(u) space (where *u* is the number of unique keys).
- **Result**: A dictionary of counts. This is the "fast" way to count frequencies compared to the brute-force baseline.
