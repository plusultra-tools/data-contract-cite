"""Validation gate: enforce citation requirements against a contract + annotations.

Rules:
  1. Every field with pii=True MUST have at least one annotation entry.
     Violation exits non-zero unless --allow-uncited is set.
  2. Every regulation referenced in annotations MUST appear in the bundled
     citation map, OR the excerpt_type must be 'paraphrase'.

Returns a ValidationResult with separate lists of errors and warnings.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from data_contract_cite.annotations import AnnotationsFile, ExcerptType
from data_contract_cite.citation_map import is_regulation_known
from data_contract_cite.contract import OdcsContract


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def __str__(self) -> str:
        parts: list[str] = []
        for e in self.errors:
            parts.append(f"ERROR: {e}")
        for w in self.warnings:
            parts.append(f"WARN:  {w}")
        return "\n".join(parts) if parts else "OK: no validation issues."


def validate(
    contract: OdcsContract,
    annotations: AnnotationsFile,
    *,
    allow_uncited: bool = False,
) -> ValidationResult:
    """Run all validation gates.

    Parameters
    ----------
    contract:
        Parsed ODCS contract.
    annotations:
        Parsed annotations file.
    allow_uncited:
        If True, downgrade 'pii field with no citation' from error to warning.

    Returns
    -------
    ValidationResult with .errors and .warnings populated.
    """
    result = ValidationResult()

    # Rule 1: every pii=True field must have at least one citation.
    for qname, _ in contract.pii_fields():
        cites = annotations.citations_for(qname)
        if not cites:
            msg = (
                f"Field '{qname}' is marked pii=true but has no annotation "
                f"in the annotations file."
            )
            if allow_uncited:
                result.warnings.append(msg)
            else:
                result.errors.append(msg)

    # Rule 2: every regulation in annotations must be known OR be paraphrase.
    for field_path, cites in annotations.fields.items():
        for cite in cites:
            if not is_regulation_known(cite.regulation):
                if cite.excerpt_type == ExcerptType.PARAPHRASE:
                    result.warnings.append(
                        f"Field '{field_path}': regulation '{cite.regulation}' is not "
                        f"in the bundled citation map (allowed because excerpt_type=paraphrase)."
                    )
                else:
                    result.errors.append(
                        f"Field '{field_path}': regulation '{cite.regulation}' is not "
                        f"in the bundled citation map. Either add it to citation_map.yaml "
                        f"or use excerpt_type: paraphrase."
                    )

    # Advisory: warn about annotations for fields that don't exist in the contract.
    contract_fields = {qname for qname, _ in contract.all_fields()}
    for field_path in annotations.all_field_paths():
        if field_path not in contract_fields:
            result.warnings.append(
                f"Annotations reference field '{field_path}' which does not exist "
                f"in the contract schema."
            )

    return result
