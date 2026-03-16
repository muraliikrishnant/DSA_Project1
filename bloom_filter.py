from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from dataclasses import field


def _u64_from_digest(digest: bytes, start: int) -> int:
    return int.from_bytes(digest[start : start + 8], "little", signed=False)


@dataclass(slots=True)
class BloomFilter:
    """
    Bloom filter with m bits and k hash functions.
    Uses double hashing to derive k indices from two 64-bit hashes.
    """

    m_bits: int
    k_hashes: int
    salt: bytes = b"dsa-project1"
    _bytes: bytearray = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.m_bits <= 0:
            raise ValueError("m_bits must be > 0")
        if self.k_hashes <= 0:
            raise ValueError("k_hashes must be > 0")
        self._bytes = bytearray((self.m_bits + 7) // 8)

    def _indices(self, item: bytes) -> list[int]:
        h = hashlib.blake2b(self.salt + item, digest_size=16).digest()
        h1 = _u64_from_digest(h, 0)
        h2 = _u64_from_digest(h, 8) | 1  # odd to help cover the space
        return [((h1 + i * h2) % self.m_bits) for i in range(self.k_hashes)]

    def add(self, item: str | bytes) -> None:
        b = item.encode("utf-8") if isinstance(item, str) else item
        for idx in self._indices(b):
            byte_i = idx >> 3
            bit = idx & 7
            self._bytes[byte_i] |= 1 << bit

    def __contains__(self, item: str | bytes) -> bool:
        b = item.encode("utf-8") if isinstance(item, str) else item
        for idx in self._indices(b):
            byte_i = idx >> 3
            bit = idx & 7
            if not (self._bytes[byte_i] & (1 << bit)):
                return False
        return True

    @staticmethod
    def theoretical_fpr(m_bits: int, k_hashes: int, n_items: int) -> float:
        # (1 - e^(-k*n/m))^k
        if m_bits <= 0 or k_hashes <= 0 or n_items < 0:
            raise ValueError("Invalid parameters")
        if n_items == 0:
            return 0.0
        return (1.0 - math.exp(-(k_hashes * n_items) / m_bits)) ** k_hashes

    @staticmethod
    def optimal_k(m_bits: int, n_items: int) -> int:
        if m_bits <= 0 or n_items <= 0:
            return 1
        return max(1, int(round((m_bits / n_items) * math.log(2))))
