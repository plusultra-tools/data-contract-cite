"""Tests for data_contract_cite.enricher."""
from __future__ import annotations

from data_contract_cite.annotations import AnnotationsFile
from data_contract_cite.contract import OdcsContract
from data_contract_cite.enricher import enrich


class TestEnrich:
    def test_annotated_field_gets_citations(
        self, contract: OdcsContract, annotations: AnnotationsFile
    ) -> None:
        enriched = enrich(contract, annotations)
        schema = enriched["schema"]
        patient_obj = next(s for s in schema if s["name"] == "patient")
        email_prop = next(p for p in patient_obj["properties"] if p["name"] == "email")
        assert "regulatory_citations" in email_prop
        assert len(email_prop["regulatory_citations"]) >= 1

    def test_unannotated_field_has_no_citations(
        self, contract: OdcsContract, annotations: AnnotationsFile
    ) -> None:
        enriched = enrich(contract, annotations)
        schema = enriched["schema"]
        patient_obj = next(s for s in schema if s["name"] == "patient")
        gender_prop = next(p for p in patient_obj["properties"] if p["name"] == "gender")
        assert "regulatory_citations" not in gender_prop

    def test_original_contract_not_mutated(
        self, contract: OdcsContract, annotations: AnnotationsFile
    ) -> None:
        original_fields = [(qn, f.pii) for qn, f in contract.all_fields()]
        enrich(contract, annotations)
        after_fields = [(qn, f.pii) for qn, f in contract.all_fields()]
        assert original_fields == after_fields

    def test_citation_dict_has_regulation_article(
        self, contract: OdcsContract, annotations: AnnotationsFile
    ) -> None:
        enriched = enrich(contract, annotations)
        schema = enriched["schema"]
        clinical_obj = next(s for s in schema if s["name"] == "clinical_event")
        diag_prop = next(p for p in clinical_obj["properties"] if p["name"] == "diagnosis_code")
        cites = diag_prop["regulatory_citations"]
        regs = {c["regulation"] for c in cites}
        assert "GDPR" in regs

    def test_empty_annotations_no_citations(
        self, contract: OdcsContract, empty_annotations: AnnotationsFile
    ) -> None:
        enriched = enrich(contract, empty_annotations)
        for schema_obj in enriched["schema"]:
            for prop in schema_obj.get("properties", []):
                assert "regulatory_citations" not in prop

    def test_contract_id_preserved(
        self, contract: OdcsContract, annotations: AnnotationsFile
    ) -> None:
        enriched = enrich(contract, annotations)
        assert enriched["id"] == "patient-events-v1"
