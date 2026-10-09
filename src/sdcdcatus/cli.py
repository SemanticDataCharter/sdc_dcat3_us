"""sdcdcatus: describe published SDC models' governed data records in a DCAT-US 3.0 catalog (data.json).

    sdcdcatus write --package DIR [--package DIR ...] [--catalog catalog.yaml] [--out data.json]
    sdcdcatus write --ct-id ID [--ct-id ID ...] [--save-package DIR] [--host URL] [--out data.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from .dcatus import DeclaredInputError, load_declared, write_catalog
from sdcreader import read_model
from sdcreader import DEFAULT_HOST, PackageError, fetch_package, load_package


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="sdcdcatus", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("write", help="write a DCAT-US 3.0 catalog for one or more models")
    w.add_argument("--package", action="append", default=[], help="directory holding dm-<ct>.jsonld and dm-<ct>.xsd (repeatable)")
    w.add_argument("--ct-id", action="append", default=[], help="published model identifier to fetch from the public catalog (repeatable)")
    w.add_argument("--save-package", help="with --ct-id: save each fetched package under this directory")
    w.add_argument("--host", default=DEFAULT_HOST)
    w.add_argument("--catalog", help="declared input (default: the package's catalog.yaml with contact@axius-sdc.com)")
    w.add_argument("--contact-name")
    w.add_argument("--contact-email")
    w.add_argument("--out", help="output file (default stdout)")
    w.add_argument("--date", help="the inventoried date, YYYY-MM-DD (default today)")
    a = p.parse_args(argv)
    if not a.package and not a.ct_id:
        p.error("give at least one --package or --ct-id")
    try:
        declared = load_declared(a.catalog, a.contact_name, a.contact_email)
        pkgs = [load_package(d, host=a.host) for d in a.package]
        for ct in a.ct_id:
            pkgs.append(fetch_package(ct, save_to=Path(a.save_package) / ct if a.save_package else None, host=a.host))
    except (PackageError, DeclaredInputError) as e:
        print(f"sdcdcatus: {e}", file=sys.stderr)
        return 2
    catalog = write_catalog([read_model(pkg) for pkg in pkgs], declared, today=date.fromisoformat(a.date) if a.date else None)
    text = json.dumps(catalog, indent=1, ensure_ascii=False)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"wrote {a.out}: {len(catalog['dataset'])} dataset(s)", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
