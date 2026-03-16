from __future__ import annotations

import csv
import gzip
import os
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path


def _open_text(path: Path):
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8", errors="replace", newline="")
    return open(path, "r", encoding="utf-8", errors="replace", newline="")


def iter_cicids_keys(dataset_dir: str | os.PathLike[str], *, column: str) -> Iterator[str]:
    """
    Iterate keys from CICIDS flow CSVs.

    Note: Many CICIDS flow exports omit IP columns; you can still benchmark by
    choosing a key column like 'Destination Port' or 'Label'.
    """
    d = Path(dataset_dir)
    if not d.exists():
        raise FileNotFoundError(d)
    files = sorted([p for p in d.glob("*.csv") if p.is_file()])
    if not files:
        raise FileNotFoundError(f"No .csv files found in {d}")

    normalized_target = column.strip().lower()
    for p in files:
        with _open_text(p) as f:
            reader = csv.reader(f)
            try:
                header_raw = next(reader)
            except StopIteration:
                continue
            header = [h.strip() for h in header_raw]
            header_map = {name.lower(): i for i, name in enumerate(header)}
            if normalized_target not in header_map:
                available = ", ".join(header[:10]) + (" ..." if len(header) > 10 else "")
                raise ValueError(f"CICIDS column {column!r} not found in {p.name}. Columns: {available}")
            idx = header_map[normalized_target]

            for row in reader:
                if idx >= len(row):
                    continue
                key = row[idx].strip()
                if key:
                    yield key


_KDD99_FIELDS: dict[str, int] = {
    "duration": 0,
    "protocol_type": 1,
    "protocol": 1,
    "service": 2,
    "flag": 3,
    "label": 41,
}


def iter_kdd99_keys(dataset_path: str | os.PathLike[str], *, field: str | int) -> Iterator[str]:
    """
    Iterate keys from KDD Cup 99 CSV-style files (no header, 42 comma-separated fields).
    """
    p = Path(dataset_path)
    if not p.exists():
        raise FileNotFoundError(p)

    if isinstance(field, str):
        key = field.strip().lower()
        if key.isdigit():
            idx = int(key)
        else:
            if key not in _KDD99_FIELDS:
                raise ValueError(f"Unknown KDD99 field {field!r}. Use one of: {sorted(_KDD99_FIELDS)} or a numeric index.")
            idx = _KDD99_FIELDS[key]
    else:
        idx = int(field)

    if idx < 0:
        raise ValueError("KDD99 index must be >= 0")

    with _open_text(p) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if idx >= len(parts):
                continue
            v = parts[idx].strip()
            if v:
                yield v


@dataclass(frozen=True)
class LoadedDataset:
    keys: list[str]
    source: str


def load_keys(dataset: str, dataset_path: str, *, limit: int, cicids_column: str, kdd99_field: str) -> LoadedDataset:
    if limit < 0:
        raise ValueError("limit must be >= 0")
    ds = dataset.strip().lower()

    if ds == "cicids":
        it = iter_cicids_keys(dataset_path, column=cicids_column)
        source = f"cicids:{dataset_path} column={cicids_column!r}"
    elif ds == "kdd99":
        it = iter_kdd99_keys(dataset_path, field=kdd99_field)
        source = f"kdd99:{dataset_path} field={kdd99_field!r}"
    else:
        raise ValueError("dataset must be 'cicids' or 'kdd99'")

    keys: list[str] = []
    if limit == 0:
        return LoadedDataset(keys=keys, source=source)

    for k in it:
        keys.append(k)
        if len(keys) >= limit:
            break
    return LoadedDataset(keys=keys, source=source)

