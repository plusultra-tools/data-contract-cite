"""SHA-256 audit chain.

Mirrors the dcm-anon pattern:
  - hash each input and output file independently
  - write an audit.sha256 file with one '<hash>  <filename>' line per artifact
  - verify: recompute and compare

Audit chain covers:
  - source contract YAML bytes
  - annotation YAML bytes
  - enriched contract YAML (output)
  - evidence JSON (output)
  - evidence Markdown (output)
  - citation_map.yaml (rules snapshot)
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    """Return SHA-256 hex of a file's contents."""
    return sha256_bytes(path.read_bytes())


def build_audit_text(entries: list[tuple[str, str]]) -> str:
    """Build the content of audit.sha256.

    Parameters
    ----------
    entries:
        List of (sha256_hex, filename) tuples, in a stable order.
    """
    return "".join(f"{digest}  {filename}\n" for digest, filename in entries)


def write_audit_file(
    audit_path: Path,
    entries: list[tuple[str, str]],
) -> str:
    """Write audit.sha256 and return its text content."""
    text = build_audit_text(entries)
    audit_path.write_text(text, encoding="utf-8")
    return text


def verify_audit_file(
    audit_path: Path,
    base_dir: Path,
) -> dict[str, Any]:
    """Re-read audit.sha256 and verify each listed file's current hash.

    For each entry:
    - If the recorded filename is an absolute path, use it directly.
    - Otherwise, resolve relative to base_dir.

    Returns a dict:
      {
        "ok": bool,
        "results": [{"filename": str, "expected": str, "actual": str|None, "match": bool}]
      }
    """
    text = audit_path.read_text(encoding="utf-8")
    results: list[dict[str, Any]] = []
    all_ok = True
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2:
            continue
        expected_hash, filename = parts
        candidate = Path(filename)
        file_path = candidate if candidate.is_absolute() else base_dir / filename
        if not file_path.exists():
            results.append(
                {"filename": filename, "expected": expected_hash, "actual": None, "match": False}
            )
            all_ok = False
            continue
        actual_hash = sha256_file(file_path)
        match = actual_hash == expected_hash
        results.append(
            {"filename": filename, "expected": expected_hash, "actual": actual_hash, "match": match}
        )
        if not match:
            all_ok = False
    return {"ok": all_ok, "results": results}
