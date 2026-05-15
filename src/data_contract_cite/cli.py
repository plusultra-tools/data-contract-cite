"""CLI entrypoint: `dc-cite`.

Subcommands:
  annotate  -- generate enriched contract + evidence pack from contract + annotations
  validate  -- verify an existing audit.sha256 chain
  manifest  -- dump the bundled citation-rules database

Exit codes:
  0 -- success
  1 -- validation error (uncited PII field, unknown regulation, etc.)
  2 -- usage / argument error
  3 -- I/O error (file not found, parse error, write error)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

from data_contract_cite import __version__
from data_contract_cite.annotations import AnnotationsFile
from data_contract_cite.audit import sha256_file, sha256_text, verify_audit_file, write_audit_file
from data_contract_cite.citation_map import citation_map_sha256, get_all_citations
from data_contract_cite.contract import OdcsContract
from data_contract_cite.enricher import enrich
from data_contract_cite.evidence import (
    build_manifest,
    render_manifest_json,
    render_manifest_md,
)
from data_contract_cite.validator import validate

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
        result: dict[str, Any] = yaml.safe_load(text)
        return result
    except FileNotFoundError:
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        raise
    except yaml.YAMLError as exc:
        print(f"ERROR: YAML parse error in {path}: {exc}", file=sys.stderr)
        raise


def _parse_contract(path: Path) -> OdcsContract:
    data = _load_yaml(path)
    return OdcsContract.model_validate(data)


def _parse_annotations(path: Path) -> AnnotationsFile:
    data = _load_yaml(path)
    return AnnotationsFile.model_validate(data)


# ---------------------------------------------------------------------------
# Sub-command: annotate
# ---------------------------------------------------------------------------


def _cmd_annotate(args: argparse.Namespace) -> int:
    contract_path = Path(args.contract)
    annotations_path = Path(args.annotations)
    out_dir = Path(args.out)

    try:
        contract = _parse_contract(contract_path)
        annotations = _parse_annotations(annotations_path)
    except (FileNotFoundError, yaml.YAMLError):
        return 3
    except Exception as exc:
        print(f"ERROR: model validation failed: {exc}", file=sys.stderr)
        return 3

    result = validate(contract, annotations, allow_uncited=args.allow_uncited)
    if result.warnings:
        for w in result.warnings:
            print(f"WARN:  {w}", file=sys.stderr)
    if not result.ok:
        for e in result.errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"ERROR: cannot create output directory {out_dir}: {exc}", file=sys.stderr)
        return 3

    # Enriched contract
    enriched_dict = enrich(contract, annotations)
    enriched_yaml = yaml.dump(enriched_dict, allow_unicode=True, sort_keys=False)
    enriched_name = f"{contract.id}-enriched.yaml"
    enriched_path = out_dir / enriched_name
    # Write as binary to avoid platform CRLF expansion (ensures hash reproducibility).
    enriched_path.write_bytes(enriched_yaml.encode("utf-8"))

    # Evidence manifest
    manifest = build_manifest(contract, annotations)
    evidence_json_text = render_manifest_json(manifest)
    evidence_md_text = render_manifest_md(manifest)
    evidence_json_path = out_dir / "dc_evidence.json"
    evidence_md_path = out_dir / "dc_evidence.md"
    evidence_json_path.write_bytes(evidence_json_text.encode("utf-8"))
    evidence_md_path.write_bytes(evidence_md_text.encode("utf-8"))

    # Audit chain
    # Input files are referenced by their absolute path so validate can find them
    # regardless of the cwd at verification time.
    # Outputs are referenced by filename (relative to the output dir).
    audit_entries = [
        (sha256_file(contract_path), str(contract_path.resolve())),
        (sha256_file(annotations_path), str(annotations_path.resolve())),
        (sha256_text(enriched_yaml), enriched_name),
        (sha256_text(evidence_json_text), "dc_evidence.json"),
        (sha256_text(evidence_md_text), "dc_evidence.md"),
    ]
    # Record citation_map hash as a comment-style metadata line (not verifiable as a file)
    citation_map_text = f"# citation_map_sha256: {citation_map_sha256()}\n"
    audit_path = out_dir / "audit.sha256"
    audit_text = write_audit_file(audit_path, audit_entries)
    # Append citation_map hash as a comment for provenance (not verified as a file)
    audit_path.write_text(audit_text + citation_map_text, encoding="utf-8")

    print(f"OK: evidence pack written to {out_dir}/")
    print(f"  {enriched_name}")
    print(f"  dc_evidence.json  (sha256={sha256_text(evidence_json_text)[:12]}...)")
    print("  dc_evidence.md")
    print("  audit.sha256")
    return 0


# ---------------------------------------------------------------------------
# Sub-command: validate
# ---------------------------------------------------------------------------


def _cmd_validate(args: argparse.Namespace) -> int:
    audit_path = Path(args.audit)
    base_dir = audit_path.parent

    if not audit_path.exists():
        print(f"ERROR: audit file not found: {audit_path}", file=sys.stderr)
        return 3

    verification = verify_audit_file(audit_path, base_dir)
    all_ok = verification["ok"]
    results: list[dict[str, Any]] = verification["results"]

    for row in results:
        status = "OK" if row["match"] else "FAIL"
        if row["actual"] is None:
            print(f"  {status}  {row['filename']}  (file not found)")
        else:
            print(f"  {status}  {row['filename']}")

    if all_ok:
        print("OK: all hashes match — manifest is current.")
        return 0
    else:
        print("FAIL: hash mismatch — manifest may be stale or tampered.", file=sys.stderr)
        return 1


# ---------------------------------------------------------------------------
# Sub-command: manifest
# ---------------------------------------------------------------------------


def _cmd_manifest(args: argparse.Namespace) -> int:
    citations = get_all_citations()
    if getattr(args, "json", False):
        print(json.dumps(citations, indent=2, sort_keys=True))
    else:
        print(yaml.dump({"citations": citations}, allow_unicode=True, sort_keys=False))
    return 0


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dc-cite",
        description=(
            "data-contract-cite: add a verbatim regulatory citation layer "
            "(GDPR / HIPAA / EHDS / CRA) to ODCS contracts."
        ),
    )
    p.add_argument("--version", action="version", version=f"dc-cite {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    # annotate
    ann = sub.add_parser(
        "annotate",
        help="Generate enriched contract + evidence pack from a contract + annotations YAML.",
    )
    ann.add_argument("--contract", required=True, help="Path to the ODCS contract YAML.")
    ann.add_argument(
        "--annotations",
        required=True,
        help="Path to the annotations YAML mapping fields to regulatory citations.",
    )
    ann.add_argument(
        "--out",
        required=True,
        help="Output directory for enriched contract, evidence pack, and audit.sha256.",
    )
    ann.add_argument(
        "--allow-uncited",
        action="store_true",
        default=False,
        help="Downgrade 'pii field with no citation' from error to warning.",
    )

    # validate
    val = sub.add_parser(
        "validate",
        help="Verify an audit.sha256 chain against the files in its directory.",
    )
    val.add_argument("audit", help="Path to the audit.sha256 file to verify.")

    # manifest
    mf = sub.add_parser(
        "manifest",
        help="Dump the bundled citation-rules database (provenance audit).",
    )
    mf.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Emit JSON instead of YAML.",
    )

    return p


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "annotate":
        return _cmd_annotate(args)
    if args.command == "validate":
        return _cmd_validate(args)
    if args.command == "manifest":
        return _cmd_manifest(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
