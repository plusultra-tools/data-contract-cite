"""Evidence manifest builder.

Produces:
  - dc_evidence.json  (machine-readable per-field citation manifest)
  - dc_evidence.md    (human-readable rendering)
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from data_contract_cite import __version__
from data_contract_cite.annotations import AnnotationsFile
from data_contract_cite.contract import OdcsContract


def _isoformat_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_manifest(
    contract: OdcsContract,
    annotations: AnnotationsFile,
    *,
    timestamp_iso: str | None = None,
) -> dict[str, Any]:
    """Build the evidence manifest dict.

    Parameters
    ----------
    contract:
        Parsed ODCS contract.
    annotations:
        Parsed annotations.
    timestamp_iso:
        Override timestamp (injectable for deterministic tests).
    """
    ts = timestamp_iso or _isoformat_now()

    field_entries: list[dict[str, Any]] = []
    for qname, field in contract.all_fields():
        cites = annotations.citations_for(qname)
        entry: dict[str, Any] = {
            "field_path": qname,
            "pii": field.pii,
            "logical_type": field.logicalType,
            "classification": field.classification,
            "citations": [c.to_dict() for c in cites],
        }
        field_entries.append(entry)

    manifest: dict[str, Any] = {
        "tool": "data-contract-cite",
        "tool_version": __version__,
        "generated_at_utc": ts,
        "contract_id": contract.id,
        "contract_version": contract.version,
        "contract_name": contract.name,
        "fields": field_entries,
    }
    return manifest


def render_manifest_json(manifest: dict[str, Any]) -> str:
    """Serialise manifest to sorted, indented JSON."""
    return json.dumps(manifest, indent=2, sort_keys=True)


def render_manifest_md(manifest: dict[str, Any]) -> str:
    """Human-readable Markdown rendering of the evidence manifest."""
    lines: list[str] = []
    lines.append("# Regulatory citation evidence")
    lines.append("")
    lines.append(f"- **Tool**: {manifest['tool']} v{manifest['tool_version']}")
    lines.append(f"- **Generated (UTC)**: {manifest['generated_at_utc']}")
    lines.append(f"- **Contract ID**: `{manifest['contract_id']}`")
    if manifest.get("contract_name"):
        lines.append(f"- **Contract name**: {manifest['contract_name']}")
    if manifest.get("contract_version"):
        lines.append(f"- **Contract version**: {manifest['contract_version']}")
    lines.append("")

    for entry in manifest["fields"]:
        pii_marker = " *(pii)*" if entry.get("pii") else ""
        ltype = entry.get("logical_type") or ""
        cls = entry.get("classification") or ""
        meta_parts = [p for p in [ltype, cls] if p]
        meta = f" — {', '.join(meta_parts)}" if meta_parts else ""
        lines.append(f"## `{entry['field_path']}`{pii_marker}{meta}")
        cites: list[dict[str, Any]] = entry.get("citations", [])
        if cites:
            for cite in cites:
                lines.append(f"### {cite['regulation']} {cite['article']}")
                if cite.get("source_url"):
                    lines.append(f"- **Source**: {cite['source_url']}")
                lines.append(f"- **Excerpt type**: `{cite['excerpt_type']}`")
                lines.append("")
                lines.append(f"> {cite['excerpt']}")
                lines.append("")
        else:
            lines.append("*No regulatory citations.*")
            lines.append("")

    return "\n".join(lines) + "\n"
