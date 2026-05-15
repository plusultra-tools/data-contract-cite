"""Tests for data_contract_cite.cli."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from data_contract_cite.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


class TestCliAnnotate:
    def test_annotate_produces_outputs(self, tmp_path: Path) -> None:
        rc = main(
            [
                "annotate",
                "--contract", str(FIXTURES / "patient-events.contract.yaml"),
                "--annotations", str(FIXTURES / "patient-events.annotations.yaml"),
                "--out", str(tmp_path / "out"),
            ]
        )
        assert rc == 0
        out = tmp_path / "out"
        assert (out / "patient-events-v1-enriched.yaml").exists()
        assert (out / "dc_evidence.json").exists()
        assert (out / "dc_evidence.md").exists()
        assert (out / "audit.sha256").exists()

    def test_annotate_enriched_yaml_has_citations(self, tmp_path: Path) -> None:
        out = tmp_path / "out"
        main(
            [
                "annotate",
                "--contract", str(FIXTURES / "patient-events.contract.yaml"),
                "--annotations", str(FIXTURES / "patient-events.annotations.yaml"),
                "--out", str(out),
            ]
        )
        enriched_path = out / "patient-events-v1-enriched.yaml"
        data = yaml.safe_load(enriched_path.read_text(encoding="utf-8"))
        patient_obj = next(s for s in data["schema"] if s["name"] == "patient")
        email_prop = next(p for p in patient_obj["properties"] if p["name"] == "email")
        assert "regulatory_citations" in email_prop

    def test_annotate_missing_contract_exits_3(self, tmp_path: Path) -> None:
        rc = main(
            [
                "annotate",
                "--contract", str(tmp_path / "nonexistent.yaml"),
                "--annotations", str(FIXTURES / "patient-events.annotations.yaml"),
                "--out", str(tmp_path / "out"),
            ]
        )
        assert rc == 3

    def test_annotate_missing_pii_citation_exits_1(self, tmp_path: Path) -> None:
        # Contract with pii=true field, empty annotations
        contract_path = tmp_path / "c.yaml"
        annotations_path = tmp_path / "a.yaml"
        contract_path.write_text(
            "apiVersion: v3.0.0\nkind: DataContract\nid: test-v1\n"
            "schema:\n  - name: t\n    properties:\n      - name: email\n        pii: true\n",
            encoding="utf-8",
        )
        annotations_path.write_text("fields: {}\n", encoding="utf-8")
        rc = main(
            [
                "annotate",
                "--contract", str(contract_path),
                "--annotations", str(annotations_path),
                "--out", str(tmp_path / "out"),
            ]
        )
        assert rc == 1

    def test_annotate_allow_uncited_exits_0(self, tmp_path: Path) -> None:
        contract_path = tmp_path / "c.yaml"
        annotations_path = tmp_path / "a.yaml"
        contract_path.write_text(
            "apiVersion: v3.0.0\nkind: DataContract\nid: test-v1\n"
            "schema:\n  - name: t\n    properties:\n      - name: email\n        pii: true\n",
            encoding="utf-8",
        )
        annotations_path.write_text("fields: {}\n", encoding="utf-8")
        rc = main(
            [
                "annotate",
                "--contract", str(contract_path),
                "--annotations", str(annotations_path),
                "--out", str(tmp_path / "out"),
                "--allow-uncited",
            ]
        )
        assert rc == 0


class TestCliValidate:
    def _produce_audit(self, tmp_path: Path) -> Path:
        out = tmp_path / "out"
        main(
            [
                "annotate",
                "--contract", str(FIXTURES / "patient-events.contract.yaml"),
                "--annotations", str(FIXTURES / "patient-events.annotations.yaml"),
                "--out", str(out),
            ]
        )
        return out / "audit.sha256"

    def test_validate_fresh_audit_exits_0(self, tmp_path: Path) -> None:
        audit_path = self._produce_audit(tmp_path)
        rc = main(["validate", str(audit_path)])
        assert rc == 0

    def test_validate_missing_audit_file_exits_3(self, tmp_path: Path) -> None:
        rc = main(["validate", str(tmp_path / "nonexistent.sha256")])
        assert rc == 3

    def test_validate_tampered_exits_1(self, tmp_path: Path) -> None:
        audit_path = self._produce_audit(tmp_path)
        # Tamper with enriched file
        enriched = tmp_path / "out" / "patient-events-v1-enriched.yaml"
        enriched.write_text(enriched.read_text(encoding="utf-8") + "\n# tampered\n", encoding="utf-8")
        rc = main(["validate", str(audit_path)])
        assert rc == 1


class TestCliManifest:
    def test_manifest_exits_0(self) -> None:
        rc = main(["manifest"])
        assert rc == 0

    def test_manifest_json_exits_0(self) -> None:
        rc = main(["manifest", "--json"])
        assert rc == 0


class TestCliVersion:
    def test_version_flag(self) -> None:
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])
        assert exc_info.value.code == 0
