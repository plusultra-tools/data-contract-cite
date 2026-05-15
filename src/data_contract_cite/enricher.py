"""Enricher: merges an ODCS contract with annotations.

Produces a new dict representation of the contract with an extra
'regulatory_citations' key per annotated field.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from data_contract_cite.annotations import AnnotationsFile
from data_contract_cite.contract import OdcsContract


def enrich(
    contract: OdcsContract,
    annotations: AnnotationsFile,
) -> dict[str, Any]:
    """Return a deep-copy of the contract dict with regulatory_citations injected.

    For each field that has annotations, a 'regulatory_citations' list is
    appended to the field's property dict inside schema[].properties[].

    Fields without annotations are left unchanged.
    """
    base: dict[str, Any] = deepcopy(contract.to_dict())

    schema_list: list[dict[str, Any]] = base.get("schema", [])
    for schema_obj in schema_list:
        props: list[dict[str, Any]] = schema_obj.get("properties", [])
        schema_name: str = schema_obj.get("name", "")
        for prop in props:
            field_name: str = prop.get("name", "")
            qname = f"{schema_name}.{field_name}"
            cites = annotations.citations_for(qname)
            if cites:
                prop["regulatory_citations"] = [c.to_dict() for c in cites]

    return base
