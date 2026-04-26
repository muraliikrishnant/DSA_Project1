# About: bloom_filter.py

## Overview
This file implements a **Bloom Filter**, a space-efficient probabilistic data structure used to test whether an element is a member of a set. It may return false positives (saying an item is in the set when it's not) but never false negatives (if it says it's not there, it's definitely not).

## How it was written
The implementation uses **double hashing** to derive *k* hash functions from just two 64-bit hash values. This is an optimization that avoids the overhead of computing *k* independent hashes. It uses `hashlib.blake2b` for the base hash.

## Key Classes and Functions

### `_u64_from_digest(digest, start)`
- **What it does**: Converts 8 bytes from a cryptographic digest into a 64-bit unsigned integer.
- **Why**: To provide the raw numbers used in the double-hashing formula.

### `BloomFilter` (Class)
- **Variables**:
    - `m_bits`: Total number of bits in the bit array.
    - `k_hashes`: Number of hash functions (indices) per item.
    - `salt`: A byte string prefixed to the item before hashing to prevent predictable collision attacks.
    - `_bytes`: The actual storage for bits, implemented as a `bytearray`.

- **Methods**:
    - `__post_init__`: Initializes the `_bytes` array size based on `m_bits`.
    - `_indices(item)`: Generates *k* indices for the given item using the double-hashing formula: `(h1 + i * h2) % m_bits`.
    - `add(item)`: Sets the bits at all *k* indices to `1`.
    - `__contains__(item)`: Checks if the bits at all *k* indices are `1`. If any bit is `0`, the item is definitely not in the set.
    - `theoretical_fpr(m, k, n)`: Calculates the expected False Positive Rate (FPR) based on the filter size, hash count, and number of items inserted.
    - `optimal_k(m, n)`: Recommends the best number of hashes *k* to minimize false positives for a given bit array size *m* and number of items *n*.

## Result & Significance
- **Result**: A fast, O(1) membership test.
- **Meaning**: In intrusion detection, this allows for checking if a packet's source IP is on a blacklist of millions of entries using very little memory and constant time.
