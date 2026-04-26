# About: Sorting, Ranking, and Top-K Selection

This documentation covers the algorithms used to rank items by their frequency. In all cases, the primary sort key is the count (descending), and the tie-breaker is the key itself (ascending).

## 1. Randomized Quick Sort (`quicksort.py`)
- **What it is**: An in-place, randomized sorting algorithm.
- **How it's written**: 
    - Uses a randomized pivot to avoid the worst-case O(n^2) performance on sorted data.
    - Implemented iteratively with a stack to keep memory usage low and avoid recursion depth issues.
    - Uses "smaller-partition-first" logic for better stack efficiency.
- **Key Function**: `quicksort_in_place(items)`
- **Complexity**: Average O(n log n), worst-case O(n^2).
- **Result**: Rearranges the input list in descending order of frequency.

## 2. Bottom-Up Merge Sort (`mergesort.py`)
- **What it is**: A stable, non-recursive sorting algorithm.
- **How it's written**:
    - Iteratively merges sub-lists of increasing width (1, 2, 4, 8...).
    - Uses two buffers (`src` and `dst`) to avoid repeated small allocations.
    - Ensures stability, meaning items with the same count and key maintain their relative order.
- **Key Function**: `mergesort(items)`
- **Complexity**: Guaranteed O(n log n) time.
- **Result**: Produces a new sorted list from the input data.

## 3. Heap-Based Top-K (`heap_topk.py`)
- **What it is**: An algorithm to find the top *K* most frequent items without sorting everything.
- **How it's written**:
    - Maintains a min-heap of size *K* (based on the ranking priority).
    - If a new item is "better" than the root of the heap (the current K-th best), the root is replaced and the heap is updated.
    - Implements `_sift_up` and `_sift_down` from scratch.
- **Key Function**: `top_k(items, k)`
- **Complexity**: O(n log K) time and O(K) extra space.
- **Result**: A sorted list of only the top *K* items. Much faster than sorting when *K* is small.

## 4. Brute-Force Counting (`bruteforce.py`)
- **What it is**: An intentionally slow baseline for performance comparison.
- **How it's written**:
    - For each item in the logs, it scans the entire list again to count occurrences.
    - Does *not* use a hash table.
- **Key Function**: `count_bruteforce(logs)`
- **Complexity**: O(n^2).
- **Result**: A list of (key, count) pairs. Used in benchmarks to show why O(n^2) is unacceptable for large network logs.
