"""Pydantic models for the annotations YAML.

Annotations file format:
  fields:
    <field_path>:
      - regulation: GDPR
        article: "Art. 9(1)"
        excerpt: "Processing of personal data revealing..."
        excerpt_type: verbatim_oj   # verbatim_oj | verbatim_cfr | paraphrase
        source_url: "https://eur-lex.europa.eu/..."

field_path MUST match <schema_object_name>.<field_name> as it appears in the contract.
"""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ExcerptType(str, Enum):
    VERBATIM_OJ = "verbatim_oj"
    VERBATIM_CFR = "verbatim_cfr"
    PARAPHRASE = "paraphrase"


class CitationEntry(BaseModel):
    """One regulatory citation for a single field."""

    regulation: str
    article: str
    excerpt: str
    excerpt_type: ExcerptType = ExcerptType.VERBATIM_OJ
    source_url: str | None = None

    model_config = {"extra": "forbid"}

    def to_dict(self) -> dict[str, Any]:
        d = self.model_dump(exclude_none=True)
        # Ensure excerpt_type is a plain string (not an Enum instance)
        if "excerpt_type" in d:
            d["excerpt_type"] = str(d["excerpt_type"])
        return d


class AnnotationsFile(BaseModel):
    """Top-level annotations YAML model."""

    fields: dict[str, list[CitationEntry]] = Field(default_factory=dict)

    model_config = {"extra": "forbid"}

    def citations_for(self, field_path: str) -> list[CitationEntry]:
        """Return citations for a given field path (e.g. 'patient.email')."""
        return self.fields.get(field_path, [])

    def all_field_paths(self) -> list[str]:
        return list(self.fields.keys())
