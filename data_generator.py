from __future__ import annotations

import bisect
import random
from collections.abc import Iterator


def _make_ipv4_pool(rng: random.Random, num_ips: int) -> list[str]:
    if num_ips <= 0:
        raise ValueError("num_ips must be > 0")
    # NOTE: This rejection-sampling loop is effectively guaranteed to terminate
    # quickly for this project (e.g., num_ips ~ 1e3). It would get slow only if
    # num_ips approached the IPv4 space size due to collisions.
    pool: list[str] = []
    seen: set[str] = set()
    while len(pool) < num_ips:
        ip = f"{rng.randint(1,254)}.{rng.randint(0,255)}.{rng.randint(0,255)}.{rng.randint(1,254)}"
        if ip in seen:
            continue
        seen.add(ip)
        pool.append(ip)
    return pool


def generate_uniform_keys(n: int, *, num_ips: int = 1000, seed: int = 0) -> Iterator[str]:
    """
    Uniform synthetic "log keys": choose uniformly from a fixed pool of IPv4 strings.
    """
    if n < 0:
        raise ValueError("n must be >= 0")
    rng = random.Random(seed)
    pool = _make_ipv4_pool(rng, num_ips)
    for _ in range(n):
        yield pool[rng.randrange(len(pool))]


def generate_zipf_keys(
    n: int,
    *,
    num_ips: int = 1000,
    alpha: float = 1.2,
    seed: int = 0,
) -> Iterator[str]:
    """
    Zipf-like skewed synthetic keys (heavy hitters dominate), without numpy.

    - `alpha` controls skew: higher => more concentrated top keys.
    """
    if n < 0:
        raise ValueError("n must be >= 0")
    if num_ips <= 0:
        raise ValueError("num_ips must be > 0")
    if alpha <= 0:
        raise ValueError("alpha must be > 0")

    rng = random.Random(seed)
    pool = _make_ipv4_pool(rng, num_ips)

    # Precompute CDF for weights proportional to 1 / i^alpha (i=1..num_ips).
    weights = [1.0 / ((i + 1) ** alpha) for i in range(num_ips)]
    total = sum(weights) or 1.0
    cdf: list[float] = []
    acc = 0.0
    for w in weights:
        acc += w / total
        cdf.append(acc)
    cdf[-1] = 1.0

    for _ in range(n):
        r = rng.random()
        idx = bisect.bisect_left(cdf, r)
        yield pool[idx]


def generate_hotspot_keys(
    n: int,
    *,
    num_ips: int = 1000,
    hot_fraction: float = 0.05,
    hot_traffic_share: float = 0.8,
    seed: int = 0,
) -> Iterator[str]:
    """
    Two-group skew model: hot_fraction of IPs generates hot_traffic_share of traffic.

    This is an explicit "5% of IPs generate 80% of traffic" style generator.
    """
    if n < 0:
        raise ValueError("n must be >= 0")
    if num_ips <= 0:
        raise ValueError("num_ips must be > 0")
    if not 0.0 < hot_fraction <= 1.0:
        raise ValueError("hot_fraction must be in (0, 1]")
    if not 0.0 < hot_traffic_share <= 1.0:
        raise ValueError("hot_traffic_share must be in (0, 1]")

    rng = random.Random(seed)
    pool = _make_ipv4_pool(rng, num_ips)

    hot_count = max(1, min(num_ips, int(round(num_ips * hot_fraction))))
    hot_pool = pool[:hot_count]
    cold_pool = pool[hot_count:]

    for _ in range(n):
        if not cold_pool:
            yield hot_pool[rng.randrange(len(hot_pool))]
            continue
        if rng.random() < hot_traffic_share:
            yield hot_pool[rng.randrange(len(hot_pool))]
        else:
            yield cold_pool[rng.randrange(len(cold_pool))]
