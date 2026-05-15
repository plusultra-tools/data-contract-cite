"""Pydantic models for the ODCS v3 contract subset supported by data-contract-cite.

Supported fields:
  - Top-level: apiVersion, kind, id, name, status, version, description, owner
  - schema[]: name, properties[]
  - properties[]: name, logicalType, physicalType, businessName, description,
                  pii (bool), classification, tags, nullable, required

Unsupported ODCS v3 fields (gap list — see README):
  - dataset.* (datasetName, type, physicalDataset, priorContractId, etc.)
  - quality.* (checks, SLAs, thresholds)
  - slaProperties, support, stakeholders, roles
  - servers.* (environment definitions, connection strings)
  - customProperties
  - price, termsAndConditions, systemInstance, port
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class OdcsField(BaseModel):
    """A single field (property) inside an ODCS schema object."""

    name: str
    logicalType: str | None = None
    physicalType: str | None = None
    businessName: str | None = None
    description: str | None = None
    pii: bool = False
    classification: str | None = None
    tags: list[str] = Field(default_factory=list)
    nullable: bool = True
    required: bool = False

    model_config = {"extra": "allow"}


class OdcsSchemaObject(BaseModel):
    """A schema table / entity inside the ODCS contract."""

    name: str
    description: str | None = None
    properties: list[OdcsField] = Field(default_factory=list)

    model_config = {"extra": "allow"}


class OdcsContract(BaseModel):
    """Subset of an ODCS v3 DataContract document.

    Full ODCS spec: https://github.com/bitol-io/open-data-contract-standard
    """

    apiVersion: str = "v3.0.0"
    kind: str = "DataContract"
    id: str
    name: str | None = None
    status: str | None = None
    version: str | None = None
    description: str | None = None
    owner: str | None = None
    schema_: list[OdcsSchemaObject] = Field(default_factory=list, alias="schema")

    model_config = {"extra": "allow", "populate_by_name": True}

    def all_fields(self) -> list[tuple[str, OdcsField]]:
        """Return (qualified_name, field) pairs for every field in every schema object."""
        pairs: list[tuple[str, OdcsField]] = []
        for schema_obj in self.schema_:
            for field in schema_obj.properties:
                pairs.append((f"{schema_obj.name}.{field.name}", field))
        return pairs

    def pii_fields(self) -> list[tuple[str, OdcsField]]:
        """Return only fields marked pii: true."""
        return [(qname, f) for qname, f in self.all_fields() if f.pii]

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dict (for YAML/JSON output), using 'schema' as key."""
        data: dict[str, Any] = self.model_dump(by_alias=True, exclude_none=True)
        return data
