"""Tests for data_contract_cite.evidence."""
from __future__ import annotations

import json

from data_contract_cite.annotations import AnnotationsFile
from data_contract_cite.contract import OdcsContract
from data_contract_cite.evidence import build_manifest, render_manifest_json, render_manifest_md

FIXED_TS = "2026-05-15T10:00:00Z"


class TestBuildManifest:
    def test_top_level_fields(
        self, contract: OdcsContract, annotations: AnnotationsFile
    ) -> None:
        manifest = build_manifest(contract, annotations, timestamp_iso=FIXED_TS)
        assert manifest["tool"] == "data-contract-cite"
        assert manifest["contract_id"] == "patient-events-v1"
        assert manifest["generated_at_utc"] == FIXED_TS

    def test_fields_list_populated(
        self, contract: OdcsContract, annotations: AnnotationsFile
    ) -> None:
        manifest = build_manifest(contract, annotations, timestamp_iso=FIXED_TS)
        field_paths = [f["field_path"] for f in manifest["fields"]]
        assert "patient.email" in field_paths
        assert "clinical_event.diagnosis_code" in field_paths

    def test_annotated_field_has_citations(
        self, contract: OdcsContract, annotations: AnnotationsFile
    ) -> None:
        manifest = build_manifest(contract, annotations, timestamp_iso=FIXED_TS)
        email_entry = next(f for f in manifest["fields"] if f["field_path"] == "patient.email")
        assert len(email_entry["citations"]) >= 1
        assert email_entry["citations"][0]["regulation"] == "GDPR"

    def test_unannotated_field_has_empty_citations(
        self, contract: OdcsContract, empty_annotations: AnnotationsFile
    ) -> None:
        manifest = build_manifest(contract, empty_annotations, timestamp_iso=FIXED_TS)
        for entry in manifest["fields"]:
            assert entry["citations"] == []

    def test_pii_flag_propagated(
        self, contract: OdcsContract, annotations: AnnotationsFile
    ) -> None:
        manifest = build_manifest(contract, annotations, timestamp_iso=FIXED_TS)
        email_entry = next(f for f in manifest["fields"] if f["field_path"] == "patient.email")
        gender_entry = next(f for f in manifest["fields"] if f["field_path"] == "patient.gender")
        assert email_entry["pii"] is True
        assert gender_entry["pii"] is False


class TestRenderManifestJson:
    def test_valid_json(
        self, contract: OdcsContract, annotations: AnnotationsFile
    ) -> None:
        manifest = build_manifest(contract, annotations, timestamp_iso=FIXED_TS)
        text = render_manifest_json(manifest)
        parsed = json.loads(text)
        assert parsed["contract_id"] == "patient-events-v1"

    def test_deterministic(
        self, contract: OdcsContract, annotations: AnnotationsFile
    ) -> None:
        manifest = build_manifest(contract, annotations, timestamp_iso=FIXED_TS)
        t1 = render_manifest_json(manifest)
        t2 = render_manifest_json(manifest)
        assert t1 == t2


class TestRenderManifestMd:
    def test_contains_contract_id(
        self, contract: OdcsContract, annotations: AnnotationsFile
    ) -> None:
        manifest = build_manifest(contract, annotations, timestamp_iso=FIXED_TS)
        md = render_manifest_md(manifest)
        assert "patient-events-v1" in md

    def test_contains_pii_marker(
        self, contract: OdcsContract, annotations: AnnotationsFile
    ) -> None:
        manifest = build_manifest(contract, annotations, timestamp_iso=FIXED_TS)
        md = render_manifest_md(manifest)
        assert "*(pii)*" in md

    def test_contains_regulation(
        self, contract: OdcsContract, annotations: AnnotationsFile
    ) -> None:
        manifest = build_manifest(contract, annotations, timestamp_iso=FIXED_TS)
        md = render_manifest_md(manifest)
        assert "GDPR" in md
