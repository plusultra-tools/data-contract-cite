"""Shared pytest fixtures."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from data_contract_cite.annotations import AnnotationsFile
from data_contract_cite.contract import OdcsContract

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture
def contract_path() -> Path:
    return FIXTURES_DIR / "patient-events.contract.yaml"


@pytest.fixture
def annotations_path() -> Path:
    return FIXTURES_DIR / "patient-events.annotations.yaml"


@pytest.fixture
def contract(contract_path: Path) -> OdcsContract:
    data = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    return OdcsContract.model_validate(data)


@pytest.fixture
def annotations(annotations_path: Path) -> AnnotationsFile:
    data = yaml.safe_load(annotations_path.read_text(encoding="utf-8"))
    return AnnotationsFile.model_validate(data)


@pytest.fixture
def minimal_contract() -> OdcsContract:
    """A minimal contract with one pii field and one non-pii field."""
    return OdcsContract.model_validate(
        {
            "apiVersion": "v3.0.0",
            "kind": "DataContract",
            "id": "minimal-v1",
            "schema": [
                {
                    "name": "users",
                    "properties": [
                        {"name": "email", "pii": True, "logicalType": "string"},
                        {"name": "event_type", "pii": False, "logicalType": "string"},
                    ],
                }
            ],
        }
    )


@pytest.fixture
def empty_annotations() -> AnnotationsFile:
    return AnnotationsFile.model_validate({"fields": {}})
