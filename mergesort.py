from __future__ import annotations

from typing import Iterable, Sequence

Item = tuple[object, int]  # (key, count) where key supports < comparisons


def _higher_priority(a: Item, b: Item) -> bool:
    if a[1] != b[1]:
        return a[1] > b[1]
    return a[0] < b[0]  # type: ignore[operator]


def mergesort(items: Sequence[Item]) -> list[Item]:
    """
    Stable bottom-up merge sort (guaranteed O(n log n)).
    Sort order: count descending, key ascending.
    """
    n = len(items)
    if n < 2:
        return list(items)

    src = list(items)
    dst = [src[0]] * n
    width = 1
    while width < n:
        for left in range(0, n, 2 * width):
            mid = min(left + width, n)
            right = min(left + 2 * width, n)
            i, j, k = left, mid, left

            while i < mid and j < right:
                if _higher_priority(src[i], src[j]):
                    dst[k] = src[i]
                    i += 1
                else:
                    dst[k] = src[j]
                    j += 1
                k += 1

            while i < mid:
                dst[k] = src[i]
                i += 1
                k += 1
            while j < right:
                dst[k] = src[j]
                j += 1
                k += 1

        src, dst = dst, src
        width *= 2
    return src


def mergesort_iter(items: Iterable[Item]) -> list[Item]:
    return mergesort(list(items))
