"""Tests for data_contract_cite.audit."""
from __future__ import annotations

from pathlib import Path

from data_contract_cite.audit import (
    build_audit_text,
    sha256_bytes,
    sha256_file,
    sha256_text,
    verify_audit_file,
    write_audit_file,
)


class TestSha256:
    def test_bytes_deterministic(self) -> None:
        h1 = sha256_bytes(b"hello")
        h2 = sha256_bytes(b"hello")
        assert h1 == h2

    def test_text_deterministic(self) -> None:
        h1 = sha256_text("hello")
        h2 = sha256_text("hello")
        assert h1 == h2

    def test_bytes_vs_text_utf8(self) -> None:
        assert sha256_bytes(b"hello") == sha256_text("hello")

    def test_different_inputs_different_hashes(self) -> None:
        assert sha256_text("foo") != sha256_text("bar")

    def test_sha256_file(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("content", encoding="utf-8")
        expected = sha256_text("content")
        assert sha256_file(f) == expected


class TestBuildAuditText:
    def test_format(self) -> None:
        entries = [("abc123", "file.yaml"), ("def456", "evidence.json")]
        text = build_audit_text(entries)
        lines = text.strip().splitlines()
        assert lines[0] == "abc123  file.yaml"
        assert lines[1] == "def456  evidence.json"

    def test_empty(self) -> None:
        assert build_audit_text([]) == ""


class TestWriteAndVerifyAuditFile:
    def test_roundtrip_all_match(self, tmp_path: Path) -> None:
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("alpha", encoding="utf-8")
        f2.write_text("beta", encoding="utf-8")

        entries = [(sha256_file(f1), "a.txt"), (sha256_file(f2), "b.txt")]
        audit_path = tmp_path / "audit.sha256"
        write_audit_file(audit_path, entries)

        result = verify_audit_file(audit_path, tmp_path)
        assert result["ok"] is True
        assert all(r["match"] for r in result["results"])

    def test_tampered_file_fails(self, tmp_path: Path) -> None:
        f = tmp_path / "data.yaml"
        f.write_text("original", encoding="utf-8")

        entries = [(sha256_file(f), "data.yaml")]
        audit_path = tmp_path / "audit.sha256"
        write_audit_file(audit_path, entries)

        # Tamper
        f.write_text("tampered", encoding="utf-8")

        result = verify_audit_file(audit_path, tmp_path)
        assert result["ok"] is False
        assert not result["results"][0]["match"]

    def test_missing_file_fails(self, tmp_path: Path) -> None:
        entries = [("deadbeef" * 8, "missing.yaml")]
        audit_path = tmp_path / "audit.sha256"
        write_audit_file(audit_path, entries)

        result = verify_audit_file(audit_path, tmp_path)
        assert result["ok"] is False
        assert result["results"][0]["actual"] is None
