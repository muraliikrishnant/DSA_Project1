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
