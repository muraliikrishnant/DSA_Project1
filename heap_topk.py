from __future__ import annotations

from typing import Iterable

Item = tuple[object, int]  # (key, count) where key supports < comparisons


def _better(a: Item, b: Item) -> bool:
    # True if a should rank ahead of b.
    if a[1] != b[1]:
        return a[1] > b[1]
    return a[0] < b[0]  # type: ignore[operator]


def _worse(a: Item, b: Item) -> bool:
    # True if a should be closer to the root (i.e., "worse" than b).
    if a[1] != b[1]:
        return a[1] < b[1]
    return a[0] > b[0]  # type: ignore[operator]


def _sift_up(heap: list[Item], idx: int) -> None:
    while idx > 0:
        parent = (idx - 1) // 2
        if _worse(heap[idx], heap[parent]):
            heap[idx], heap[parent] = heap[parent], heap[idx]
            idx = parent
        else:
            return


def _sift_down(heap: list[Item], idx: int) -> None:
    n = len(heap)
    while True:
        left = 2 * idx + 1
        right = left + 1
        smallest = idx

        if left < n and _worse(heap[left], heap[smallest]):
            smallest = left
        if right < n and _worse(heap[right], heap[smallest]):
            smallest = right

        if smallest == idx:
            return
        heap[idx], heap[smallest] = heap[smallest], heap[idx]
        idx = smallest


def top_k(items: Iterable[Item], k: int) -> list[Item]:
    """
    Heap-based Top-K selection.
    Returns items sorted by count descending, key ascending.
    """
    if k <= 0:
        return []

    heap: list[Item] = []
    for item in items:
        if len(heap) < k:
            heap.append(item)
            _sift_up(heap, len(heap) - 1)
            continue

        if _better(item, heap[0]):
            heap[0] = item
            _sift_down(heap, 0)

    # Avoid built-in sort for the core path; reuse our merge sort.
    from mergesort import mergesort  # local import to keep modules independent

    return mergesort(heap)
