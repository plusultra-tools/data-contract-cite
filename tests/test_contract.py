"""Tests for data_contract_cite.contract."""
from __future__ import annotations

from pathlib import Path

import yaml

from data_contract_cite.contract import OdcsContract, OdcsField, OdcsSchemaObject


class TestOdcsField:
    def test_defaults(self) -> None:
        f = OdcsField(name="email")
        assert f.name == "email"
        assert f.pii is False
        assert f.tags == []
        assert f.nullable is True
        assert f.required is False

    def test_pii_true(self) -> None:
        f = OdcsField(name="ssn", pii=True, logicalType="string")
        assert f.pii is True

    def test_extra_fields_allowed(self) -> None:
        f = OdcsField(name="x", custom_attr="something")
        assert f.name == "x"


class TestOdcsSchemaObject:
    def test_empty_properties(self) -> None:
        s = OdcsSchemaObject(name="events")
        assert s.properties == []

    def test_with_properties(self) -> None:
        s = OdcsSchemaObject(
            name="patient",
            properties=[
                OdcsField(name="email", pii=True),
                OdcsField(name="event_type", pii=False),
            ],
        )
        assert len(s.properties) == 2


class TestOdcsContract:
    def test_minimal_valid(self) -> None:
        c = OdcsContract.model_validate({"id": "test-v1", "schema": []})
        assert c.id == "test-v1"
        assert c.apiVersion == "v3.0.0"
        assert c.kind == "DataContract"

    def test_all_fields(self, contract: OdcsContract) -> None:
        pairs = contract.all_fields()
        names = [qn for qn, _ in pairs]
        assert "patient.email" in names
        assert "patient.medical_record_number" in names
        assert "clinical_event.diagnosis_code" in names

    def test_pii_fields_only(self, contract: OdcsContract) -> None:
        pii = contract.pii_fields()
        pii_names = {qn for qn, _ in pii}
        assert "patient.email" in pii_names
        assert "patient.gender" not in pii_names
        assert "clinical_event.department" not in pii_names

    def test_to_dict_uses_schema_alias(self, contract: OdcsContract) -> None:
        d = contract.to_dict()
        assert "schema" in d
        assert "schema_" not in d

    def test_load_from_fixture_file(self, contract_path: Path) -> None:
        data = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
        c = OdcsContract.model_validate(data)
        assert c.id == "patient-events-v1"
        assert c.status == "active"
        assert len(c.schema_) == 2

    def test_schema_alias_roundtrip(self) -> None:
        raw = {
            "id": "rt-v1",
            "schema": [{"name": "tbl", "properties": [{"name": "col"}]}],
        }
        c = OdcsContract.model_validate(raw)
        d = c.to_dict()
        assert "schema" in d
        assert d["schema"][0]["name"] == "tbl"
