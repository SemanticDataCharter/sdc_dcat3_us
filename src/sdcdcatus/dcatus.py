"""Emit a DCAT-US 3.0 Catalog (data.json) for one or more models.

Two kinds of input, kept apart: what the model's package carries (nothing invented), and what the catalog's publisher
declares in catalog.yaml because the schema or the statute asks for it and the package cannot know it (the contact
point, the catalog's own title and homepage, access rights). The published schema fills two slots: describedBy, the
machine-readable data dictionary OMB M-25-05 requirement B asks for, and conformsTo, the standard the records conform
to. Both cite it by URL and SHA-256.
"""
from __future__ import annotations

import re
from datetime import date
from importlib import resources

import yaml

from sdcreader import Model

SDC4_RM = "https://semanticdatacharter.com/ns/sdc4/sdc4.xsd"
PERMANENCE = "https://semanticdatacharter.com/permanence.html"
DCAT_US_STANDARD = {"@type": "Standard", "title": "DCAT-US 3.0", "identifier": "https://resources.data.gov/dcat-us/3.0.0/definitions/catalog"}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class DeclaredInputError(Exception):
    pass


def load_declared(path=None, contact_name: str | None = None, contact_email: str | None = None) -> dict:
    """The declared input: the package's default file, or the publisher's own, with command-line overrides."""
    text = open(path, encoding="utf-8").read() if path else resources.files("sdcdcatus").joinpath("data/catalog.yaml").read_text(encoding="utf-8")
    d = yaml.safe_load(text) or {}
    contact = dict(d.get("contact") or {})
    if contact_name:
        contact["name"] = contact_name
    if contact_email:
        contact["email"] = contact_email
    d["contact"] = contact
    email = (contact.get("email") or "").strip()
    if not email or not EMAIL_RE.match(email):
        raise DeclaredInputError("a contact e-mail is required (DCAT-US makes contactPoint.hasEmail mandatory); set contact.email in the catalog file or pass --contact-email")
    if not (contact.get("name") or "").strip():
        raise DeclaredInputError("a contact name is required (contactPoint.fn); set contact.name or pass --contact-name")
    return d


def write_catalog(models: list[Model], declared: dict, today: date | None = None) -> dict:
    today = today or date.today()
    cat = declared.get("catalog") or {}
    publisher = declared.get("publisher") or {}
    datasets = [_dataset(m, declared, today) for m in models]
    catalog = {
        "@type": "Catalog",
        "conformsTo": DCAT_US_STANDARD,
        "title": cat.get("title") or "Governed data records",
        "description": cat.get("description") or "",
        "publisher": _agent(publisher),
        "issued": min(d["issued"] for d in datasets) if datasets else today.isoformat(),
        "modified": max(d["modified"] for d in datasets) if datasets else today.isoformat(),
        "language": "en",
        "dataset": datasets,
    }
    if cat.get("homepage"):
        catalog["homepage"] = {"@type": "Document", "title": catalog["title"], "accessURL": cat["homepage"]}
    return catalog


def _dataset(model: Model, declared: dict, today: date) -> dict:
    pkg = model.package
    publisher = declared.get("publisher") or {}
    contact = declared["contact"]
    date_modified = (model.dc("date") or "")[:10] or today.isoformat()
    license_url = model.rights_url
    model_publisher = model.dc("publisher")
    schema_title = f"SDC4 schema dm-{model.ct_id} ({model.title})"
    ds = {
        "@id": pkg.catalog_url,
        "@type": "Dataset",
        "title": f"{model.title} governed data records",
        "description": _description(model, date_modified),
        "identifier": {"@type": "Identifier", "notation": f"dm-{model.ct_id}", "schemaAgency": model_publisher or publisher.get("name") or "Semantic Data Charter"},
        "contactPoint": {"@type": "Kind", "fn": contact["name"], "hasEmail": f"mailto:{contact['email']}"},
        "publisher": {"@type": "Organization", "name": model_publisher} if model_publisher else _organization(publisher),
        "keyword": _keywords(model),
        "landingPage": {"@type": "Document", "title": f"{model.title} in the public catalog", "accessURL": pkg.catalog_url},
        "describedBy": {
            "@type": "Distribution",
            "title": schema_title,
            "description": f"The immutable schema every {model.title} record is validated against: {len(model.leaves)} variables with their "
                           "definitions, datatypes, units, enumerated values and codes, and the sixteen typed reasons a value may be missing.",
            "downloadURL": pkg.schema_url_pinned,
            "mediaType": "application/xml",
            "format": "XSD",
            "checksum": {"@type": "Checksum", "algorithm": "SHA-256", "checksumValue": pkg.sha256},
            "conformsTo": [{"@type": "Standard", "title": "SDC4 reference model", "identifier": SDC4_RM}],
            "modified": date_modified,
        },
        "conformsTo": [{"@type": "Standard", "title": schema_title, "identifier": pkg.schema_url_pinned, "modified": date_modified}],
        "issued": date_modified,
        "modified": date_modified,
        "inventoried": today.isoformat(),
        "language": "en",
        "accessRights": declared.get("access_rights") or "public",
        "versionNotes": f"A published Semantic Data Charter model never changes; a revision is a new model naming the one it revised "
                        f"(prov:wasRevisionOf). This dataset's schema is pinned by SHA-256 {pkg.sha256}. See {PERMANENCE}.",
    }
    if license_url:
        ds["license"] = license_url
        ds["describedBy"]["license"] = license_url
    creator = model.dc("creator")
    if creator:
        ds["creator"] = {"@type": "Agent", "name": creator}
    # the rest of the model's Dublin Core, when the modeler wrote it (SDCStudio's defaults read as unset)
    if model.contributors:
        ds["contributor"] = [{"@type": "Agent", "name": c} for c in model.contributors]
    if model.subjects:
        ds["subject"] = list(model.subjects)
    coverage = model.dc("coverage")
    if coverage:
        ds["spatial"] = [{"@type": "Location", "prefLabel": coverage}]
    relation = model.dc("relation")
    if relation and re.match(r"^https?://\S+$", relation):
        ds["relation"] = [relation]
    rights = list(declared.get("rights") or [])
    if model.rights_statement:
        rights.insert(0, model.rights_statement)
    if rights:
        ds["rights"] = rights
    if declared.get("theme"):
        ds["theme"] = list(declared["theme"])
    if declared.get("distribution"):
        ds["distribution"] = list(declared["distribution"])
    return ds


def _description(model: Model, date_modified: str) -> str:
    base = model.description.strip().rstrip(".")
    return (f"{base}. Each record is a governed data record conforming to the Semantic Data Charter model {model.title} "
            f"(dm-{model.ct_id}), published {date_modified}. The schema is immutable and is the data dictionary: every variable's name, "
            f"definition, datatype, units and permitted values, cited by URL and SHA-256 in describedBy and conformsTo.")


def _keywords(model: Model) -> list[str]:
    words = model.subjects + ["Semantic Data Charter", "SDC4", "governed data record"]
    project = model.package.catalog.get("project_name")
    if project:
        words.insert(0, project)
    return words


def _agent(p: dict) -> dict:
    a = {"@type": "Agent", "name": p.get("name") or "Unknown"}
    if p.get("id"):
        a["@id"] = p["id"]
    return a


def _organization(p: dict) -> dict:
    o = {"@type": "Organization", "name": p.get("name") or "Unknown"}
    if p.get("id"):
        o["@id"] = p["id"]
    return o

