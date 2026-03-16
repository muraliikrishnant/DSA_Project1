from __future__ import annotations

from typing import Sequence

from mergesort import mergesort

Item = tuple[object, int]  # (key, count)


def count_bruteforce(logs: Sequence[object]) -> list[Item]:
    """
    Intentionally O(n^2) baseline: count frequencies by scanning the list for each
    new IP instead of using a hash table.
    """
    out: list[Item] = []
    seen: set[object] = set()
    for key in logs:
        if key in seen:
            continue
        seen.add(key)
        c = 0
        for x in logs:
            if x == key:
                c += 1
        out.append((key, c))
    return out


def rank_bruteforce(logs: Sequence[object]) -> list[Item]:
    return mergesort(count_bruteforce(logs))
