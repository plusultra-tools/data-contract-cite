"""Tests for data_contract_cite.annotations."""
from __future__ import annotations

import pytest

from data_contract_cite.annotations import AnnotationsFile, CitationEntry, ExcerptType


class TestCitationEntry:
    def test_minimal(self) -> None:
        c = CitationEntry(
            regulation="GDPR",
            article="Art. 4(1)",
            excerpt="personal data means...",
        )
        assert c.regulation == "GDPR"
        assert c.excerpt_type == ExcerptType.VERBATIM_OJ

    def test_paraphrase_type(self) -> None:
        c = CitationEntry(
            regulation="EHDS",
            article="Art. 64-72",
            excerpt="secondary use...",
            excerpt_type=ExcerptType.PARAPHRASE,
        )
        assert c.excerpt_type == ExcerptType.PARAPHRASE

    def test_to_dict_excludes_none(self) -> None:
        c = CitationEntry(regulation="GDPR", article="Art. 4(1)", excerpt="...")
        d = c.to_dict()
        assert "source_url" not in d

    def test_to_dict_includes_source_url(self) -> None:
        c = CitationEntry(
            regulation="GDPR",
            article="Art. 4(1)",
            excerpt="...",
            source_url="https://eur-lex.europa.eu/eli/reg/2016/679/oj",
        )
        d = c.to_dict()
        assert d["source_url"] == "https://eur-lex.europa.eu/eli/reg/2016/679/oj"

    def test_extra_fields_forbidden(self) -> None:
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            CitationEntry(
                regulation="GDPR",
                article="Art. 4(1)",
                excerpt="...",
                unknown_field="oops",
            )


class TestAnnotationsFile:
    def test_empty(self) -> None:
        af = AnnotationsFile.model_validate({"fields": {}})
        assert af.all_field_paths() == []

    def test_citations_for_missing(self, empty_annotations: AnnotationsFile) -> None:
        assert empty_annotations.citations_for("patient.email") == []

    def test_load_fixture(self, annotations: AnnotationsFile) -> None:
        paths = annotations.all_field_paths()
        assert "patient.email" in paths
        assert "clinical_event.diagnosis_code" in paths

    def test_citations_for_email(self, annotations: AnnotationsFile) -> None:
        cites = annotations.citations_for("patient.email")
        assert len(cites) >= 1
        assert cites[0].regulation == "GDPR"

    def test_citations_for_diagnosis(self, annotations: AnnotationsFile) -> None:
        cites = annotations.citations_for("clinical_event.diagnosis_code")
        regs = {c.regulation for c in cites}
        assert "GDPR" in regs
        assert "HIPAA" in regs
        assert "EHDS" in regs

    def test_excerpt_types_present(self, annotations: AnnotationsFile) -> None:
        all_types = {
            c.excerpt_type
            for cites in annotations.fields.values()
            for c in cites
        }
        assert ExcerptType.VERBATIM_OJ in all_types
        assert ExcerptType.PARAPHRASE in all_types
