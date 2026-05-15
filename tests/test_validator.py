"""Tests for data_contract_cite.validator."""
from __future__ import annotations

from data_contract_cite.annotations import AnnotationsFile
from data_contract_cite.contract import OdcsContract
from data_contract_cite.validator import validate


def _contract_with_pii(field_name: str = "email") -> OdcsContract:
    return OdcsContract.model_validate(
        {
            "id": "test-v1",
            "schema": [
                {
                    "name": "users",
                    "properties": [{"name": field_name, "pii": True}],
                }
            ],
        }
    )


def _annotations_with_gdpr(field_path: str) -> AnnotationsFile:
    return AnnotationsFile.model_validate(
        {
            "fields": {
                field_path: [
                    {
                        "regulation": "GDPR",
                        "article": "Art. 4(1)",
                        "excerpt": "personal data means...",
                        "excerpt_type": "verbatim_oj",
                    }
                ]
            }
        }
    )


class TestValidateRule1PiiMustHaveCitation:
    def test_pii_with_citation_ok(self) -> None:
        contract = _contract_with_pii("email")
        annotations = _annotations_with_gdpr("users.email")
        result = validate(contract, annotations)
        assert result.ok
        assert result.errors == []

    def test_pii_without_citation_error(
        self, minimal_contract: OdcsContract, empty_annotations: AnnotationsFile
    ) -> None:
        result = validate(minimal_contract, empty_annotations)
        assert not result.ok
        assert any("pii=true" in e for e in result.errors)

    def test_pii_without_citation_allow_uncited(
        self, minimal_contract: OdcsContract, empty_annotations: AnnotationsFile
    ) -> None:
        result = validate(minimal_contract, empty_annotations, allow_uncited=True)
        assert result.ok
        assert any("pii=true" in w for w in result.warnings)

    def test_non_pii_no_citation_ok(self) -> None:
        contract = OdcsContract.model_validate(
            {
                "id": "test",
                "schema": [
                    {
                        "name": "events",
                        "properties": [{"name": "event_type", "pii": False}],
                    }
                ],
            }
        )
        annotations = AnnotationsFile.model_validate({"fields": {}})
        result = validate(contract, annotations)
        assert result.ok


class TestValidateRule2KnownRegulation:
    def test_known_regulation_ok(self) -> None:
        contract = _contract_with_pii("email")
        annotations = _annotations_with_gdpr("users.email")
        result = validate(contract, annotations)
        assert result.ok

    def test_unknown_regulation_verbatim_error(self) -> None:
        contract = _contract_with_pii("email")
        annotations = AnnotationsFile.model_validate(
            {
                "fields": {
                    "users.email": [
                        {
                            "regulation": "UNKNOWN_REG_XYZ",
                            "article": "Art. 1",
                            "excerpt": "...",
                            "excerpt_type": "verbatim_oj",
                        }
                    ]
                }
            }
        )
        result = validate(contract, annotations)
        assert not result.ok
        assert any("UNKNOWN_REG_XYZ" in e for e in result.errors)

    def test_unknown_regulation_paraphrase_warning(self) -> None:
        contract = _contract_with_pii("email")
        annotations = AnnotationsFile.model_validate(
            {
                "fields": {
                    "users.email": [
                        {
                            "regulation": "LGPD",
                            "article": "Art. 6",
                            "excerpt": "...",
                            "excerpt_type": "paraphrase",
                        }
                    ]
                }
            }
        )
        result = validate(contract, annotations)
        assert result.ok
        assert any("LGPD" in w for w in result.warnings)


class TestValidateAdvisoryWarnings:
    def test_annotation_for_nonexistent_field_warns(self) -> None:
        contract = OdcsContract.model_validate(
            {"id": "test", "schema": [{"name": "t", "properties": [{"name": "x", "pii": False}]}]}
        )
        annotations = _annotations_with_gdpr("t.nonexistent_field")
        result = validate(contract, annotations)
        assert any("nonexistent_field" in w for w in result.warnings)


class TestValidateFullFixture:
    def test_full_fixture_passes(
        self, contract: OdcsContract, annotations: AnnotationsFile
    ) -> None:
        result = validate(contract, annotations)
        assert result.ok, str(result)
