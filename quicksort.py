from __future__ import annotations

import random
from typing import MutableSequence

Item = tuple[object, int]  # (key, count) where key supports < comparisons


def _higher_priority(a: Item, b: Item) -> bool:
    # Higher count first; tie-breaker: smaller IP first (lexicographic in dotted form matches int order).
    if a[1] != b[1]:
        return a[1] > b[1]
    return a[0] < b[0]  # type: ignore[operator]


def quicksort_in_place(items: MutableSequence[Item], *, seed: int | None = 0) -> None:
    """
    Randomized Quick Sort in-place on (key, count) items.
    Sort order: count descending, key ascending.
    """
    n = len(items)
    if n < 2:
        return

    rng = random.Random(seed)
    stack: list[tuple[int, int]] = [(0, n - 1)]

    while stack:
        lo, hi = stack.pop()
        if lo >= hi:
            continue

        pivot_index = rng.randint(lo, hi)
        items[pivot_index], items[hi] = items[hi], items[pivot_index]
        pivot = items[hi]

        i = lo
        for j in range(lo, hi):
            if _higher_priority(items[j], pivot):
                items[i], items[j] = items[j], items[i]
                i += 1

        items[i], items[hi] = items[hi], items[i]

        left_lo, left_hi = lo, i - 1
        right_lo, right_hi = i + 1, hi

        # Process smaller partition first to keep stack shallow.
        left_size = left_hi - left_lo
        right_size = right_hi - right_lo
        if left_size > right_size:
            if left_lo < left_hi:
                stack.append((left_lo, left_hi))
            if right_lo < right_hi:
                stack.append((right_lo, right_hi))
        else:
            if right_lo < right_hi:
                stack.append((right_lo, right_hi))
            if left_lo < left_hi:
                stack.append((left_lo, left_hi))
