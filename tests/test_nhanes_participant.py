"""The NHANES Participant catalog passes GSA's own DCAT-US 3.0 JSON Schema at the pinned commit, the snapshot proves
itself intact by passing their good and bad corpus, the schema is cited as the data dictionary and the standard by
URL and SHA-256, and the writer says only what the package and the declared input say."""
import hashlib
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from sdcdcatus import DeclaredInputError, load_declared, load_package, read_model, write_catalog

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "samples" / "nhanes-participant"
SNAPSHOT = ROOT / "data" / "dcat-us-4996591"      # GSA/dcat-us at 4996591
CT = "xy8upneajsb8vdcmnve01g6g"
DAY = date(2026, 10, 9)


@pytest.fixture(scope="module")
def registry():
    """GSA's method: a registry of every definition by its $id, as test_json_schema.py builds it."""
    reg = Registry()
    for f in (SNAPSHOT / "definitions").glob("*.json"):
        reg = Resource.from_contents(json.loads(f.read_text())) @ reg
    return reg


def validator(registry, cls):
    return Draft202012Validator({"$ref": f"https://resources.data.gov/dcat-us/3.0.0/definitions/{cls}"}, registry=registry,
                                format_checker=Draft202012Validator.FORMAT_CHECKER)


@pytest.fixture(scope="module")
def model():
    return read_model(load_package(PACKAGE))


@pytest.fixture(scope="module")
def catalog(model):
    return write_catalog([model], load_declared(), today=DAY)


def test_the_snapshot_passes_gsa_s_own_corpus():
    r = subprocess.run([sys.executable, str(SNAPSHOT / "test_json_schema.py")], capture_output=True, text=True, cwd=SNAPSHOT)
    fails = [l for l in r.stdout.splitlines() if l.startswith("FAIL")]
    assert r.returncode == 0 and not fails, (r.returncode, fails[:5], r.stdout[-800:])
    assert sum(l.startswith("PASS") for l in r.stdout.splitlines()) > 50


def test_the_catalog_and_its_dataset_pass_the_dcat_us_schema(catalog, registry):
    errors = [f"{'/'.join(map(str, e.absolute_path))}: {e.message[:160]}" for e in validator(registry, "catalog").iter_errors(catalog)]
    assert not errors, errors[:8]
    errors = [f"{'/'.join(map(str, e.absolute_path))}: {e.message[:160]}" for e in validator(registry, "dataset").iter_errors(catalog["dataset"][0])]
    assert not errors, errors[:8]
    errors = list(validator(registry, "distribution").iter_errors(catalog["dataset"][0]["describedBy"]))
    assert not errors


def test_the_schema_is_the_data_dictionary_and_the_standard_by_url_and_sha256(catalog, model):
    sha = hashlib.sha256((PACKAGE / f"dm-{CT}.xsd").read_bytes()).hexdigest()
    assert model.package.sha256 == sha == model.package.versions["current_sha256"]
    ds = catalog["dataset"][0]
    url = f"https://sdcstudio.axius-sdc.com/dmlib/dm-{CT}.xsd?sha256={sha}"
    assert ds["describedBy"]["downloadURL"] == url
    assert ds["describedBy"]["checksum"] == {"@type": "Checksum", "algorithm": "SHA-256", "checksumValue": sha}
    assert ds["describedBy"]["conformsTo"][0]["identifier"] == "https://semanticdatacharter.com/ns/sdc4/sdc4.xsd"
    assert ds["conformsTo"][0]["identifier"] == url
    assert ds["identifier"] == {"@type": "Identifier", "notation": f"dm-{CT}", "schemaAgency": "Axius SDC, Inc."}
    assert "153 variables" in ds["describedBy"]["description"] and len(model.leaves) == 153
    assert ds["language"] == "en" and ds["inventoried"] == "2026-10-09" and ds["modified"] == "2026-09-26"
    assert "distribution" not in ds   # the records are not public; stated in the README


def test_the_contact_point_is_declared_input_with_the_default_address(catalog):
    ds = catalog["dataset"][0]
    assert ds["contactPoint"] == {"@type": "Kind", "fn": "Axius SDC, Inc. data contact", "hasEmail": "mailto:contact@axius-sdc.com"}
    overridden = load_declared(None, "Agency Data Officer", "data@agency.gov")
    assert overridden["contact"] == {"name": "Agency Data Officer", "email": "data@agency.gov"}
    with pytest.raises(DeclaredInputError, match="contact e-mail"):
        load_declared(None, None, "not-an-address")


def test_the_writer_refuses_a_declared_file_with_no_contact_email(tmp_path):
    f = tmp_path / "catalog.yaml"
    f.write_text("contact:\n  name: Someone\n  email: ''\npublisher:\n  name: X\n")
    with pytest.raises(DeclaredInputError, match="contact e-mail"):
        load_declared(f)


def test_nothing_is_defaulted_for_an_agency(catalog):
    ds = catalog["dataset"][0]
    assert ds["accessRights"] == "public" and "rights" not in ds and "theme" not in ds
    assert "bureauCode" not in ds and "programCode" not in ds


def test_the_writer_refuses_a_model_without_its_package(tmp_path):
    from sdcdcatus.package import PackageError
    (tmp_path / "dm-abc.xsd").write_bytes(b"<xsd:schema/>")
    with pytest.raises(PackageError, match="missing"):
        load_package(tmp_path)
