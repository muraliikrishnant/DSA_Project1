from __future__ import annotations

import re
from typing import Iterable, TypeVar


_IPV4_RE = re.compile(r"(?:\d{1,3}\.){3}\d{1,3}")

T = TypeVar("T")

def ipv4_str_to_int(ip: str) -> int:
    parts = ip.split(".")
    if len(parts) != 4:
        raise ValueError(f"Invalid IPv4 address: {ip!r}")
    out = 0
    for part in parts:
        if not part or (len(part) > 1 and part[0] == "0" and part != "0"):
            # Avoid ambiguous forms like "001".
            raise ValueError(f"Invalid IPv4 address: {ip!r}")
        try:
            octet = int(part, 10)
        except ValueError as e:
            raise ValueError(f"Invalid IPv4 address: {ip!r}") from e
        if octet < 0 or octet > 255:
            raise ValueError(f"Invalid IPv4 address: {ip!r}")
        out = (out << 8) | octet
    return out


def ipv4_int_to_str(value: int) -> str:
    if value < 0 or value > 0xFFFFFFFF:
        raise ValueError(f"IPv4 int out of range: {value}")
    return ".".join(str((value >> shift) & 0xFF) for shift in (24, 16, 8, 0))


def extract_first_ipv4_int(line: str) -> int | None:
    """
    Best-effort extraction of the first IPv4 address in a log line.
    Returns None if no valid IPv4 is found.

    Note: IPv6 is intentionally not supported for this project.
    """
    m = _IPV4_RE.search(line)
    if not m:
        return None
    candidate = m.group(0)
    try:
        return ipv4_str_to_int(candidate)
    except ValueError:
        return None


def count_frequencies(stream: Iterable[T]) -> dict[T, int]:
    counts: dict[T, int] = {}
    for key in stream:
        counts[key] = counts.get(key, 0) + 1
    return counts
