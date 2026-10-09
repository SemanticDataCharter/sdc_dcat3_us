"""The seven FAIR Data Demo models as one data.json: a comprehensive data inventory entry per governed model, each with
its schema as the data dictionary, passing GSA's DCAT-US 3.0 schema at the pinned commit."""
import json
from datetime import date
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from sdcdcatus import load_declared, load_package, read_model, write_catalog

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "samples" / "fair-data-demo"
SNAPSHOT = ROOT / "data" / "dcat-us-4996591"
MODELS = ["xy8upneajsb8vdcmnve01g6g", "epbdfmvxc3gbh5f66hhb3o2m", "iymux9kjv8ndbkoi36xzx17i", "fnv3zi2btk3s0sfodjsc25eb",
          "ji1eccop92mlmikwq5gwp7cr", "mllwhe842wtnim4ms48qonio", "nvemvhvdkctdlm9alwwgcay7"]


@pytest.fixture(scope="module")
def registry():
    reg = Registry()
    for f in (SNAPSHOT / "definitions").glob("*.json"):
        reg = Resource.from_contents(json.loads(f.read_text())) @ reg
    return reg


def test_the_seven_model_catalog_passes_the_dcat_us_schema_and_matches_the_committed_sample(registry):
    models = [read_model(load_package(SAMPLE / ct)) for ct in MODELS]
    catalog = write_catalog(models, load_declared(), today=date(2026, 10, 9))
    v = Draft202012Validator({"$ref": "https://resources.data.gov/dcat-us/3.0.0/definitions/catalog"}, registry=registry,
                             format_checker=Draft202012Validator.FORMAT_CHECKER)
    errors = [f"{'/'.join(map(str, e.absolute_path))}: {e.message[:160]}" for e in v.iter_errors(catalog)]
    assert not errors, errors[:8]
    assert len(catalog["dataset"]) == 7
    assert [d["identifier"]["notation"] for d in catalog["dataset"]] == [f"dm-{ct}" for ct in MODELS]
    for m, d in zip(models, catalog["dataset"]):
        assert m.package.sha256 == m.package.versions["current_sha256"]
        assert d["describedBy"]["checksum"]["checksumValue"] == m.package.sha256
        assert d["contactPoint"]["hasEmail"] == "mailto:contact@axius-sdc.com"
    assert catalog == json.loads((SAMPLE / "data.json").read_text())
