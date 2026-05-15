"""Bundled regulatory citation map loader.

Loads data/citation_map.yaml and exposes lookup helpers.
"""
from __future__ import annotations

from importlib import resources
from typing import Any

import yaml


def _load_citation_map() -> list[dict[str, Any]]:
    """Load the bundled citation_map.yaml from the package data directory."""
    pkg_data = resources.files("data_contract_cite").joinpath("data/citation_map.yaml")
    text = pkg_data.read_text(encoding="utf-8")
    doc: dict[str, Any] = yaml.safe_load(text)
    result: list[dict[str, Any]] = doc.get("citations", [])
    return result


_CITATIONS: list[dict[str, Any]] | None = None


def get_all_citations() -> list[dict[str, Any]]:
    """Return all bundled citation entries (cached after first load)."""
    global _CITATIONS
    if _CITATIONS is None:
        _CITATIONS = _load_citation_map()
    return _CITATIONS


def lookup(regulation: str, article: str) -> dict[str, Any] | None:
    """Return the bundled citation entry matching regulation + article, or None."""
    reg_upper = regulation.upper()
    art_norm = article.strip()
    for entry in get_all_citations():
        if entry["regulation"].upper() == reg_upper and entry["article"].strip() == art_norm:
            return entry
    return None


def is_regulation_known(regulation: str) -> bool:
    """Return True if the regulation appears at least once in the bundled map."""
    reg_upper = regulation.upper()
    return any(e["regulation"].upper() == reg_upper for e in get_all_citations())


def citation_map_sha256() -> str:
    """Return SHA-256 of the raw citation_map.yaml bytes (for audit chain)."""
    import hashlib

    pkg_data = resources.files("data_contract_cite").joinpath("data/citation_map.yaml")
    raw = pkg_data.read_bytes()
    return hashlib.sha256(raw).hexdigest()
