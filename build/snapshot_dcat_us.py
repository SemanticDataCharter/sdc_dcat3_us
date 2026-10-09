#!/usr/bin/env python3
"""Copy the DCAT-US 3.0 JSON Schema and GSA's validation script from the read-only clone in source/ into data/, named
by the pinned commit (docs/design/sdc-dcat3-us-PRD.md, section 1). Refuses a clone that is not at the pin, so the
snapshot always says which DCAT-US it is. Their examples come too, so the snapshot proves itself intact by passing
their own good and bad corpus.

    python build/snapshot_dcat_us.py [--source DIR] [--check]
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PIN = "4996591"
REPO = "dcat-us"
FILES = ["test_json_schema.py", "README.md"]


def main(check_only: bool, source: Path) -> int:
    repo = source / REPO
    if not repo.is_dir():
        print(f"{REPO}: not cloned (git clone --quiet https://github.com/GSA/dcat-us {repo}; git -C {repo} checkout {PIN})")
        return 1
    at = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short=7", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    if at != PIN:
        print(f"{REPO}: at {at}, pinned {PIN}; re-pinning is a deliberate step (PRD section 1)")
        return 1
    print(f"{REPO}: {PIN} ok")
    if check_only:
        return 0
    js = repo / "jsonschema"
    out = ROOT / "data" / f"dcat-us-{PIN}"
    out.mkdir(parents=True, exist_ok=True)
    for f in FILES:
        shutil.copy2(js / f, out / f)
    shutil.copy2(repo / "LICENSE.md", out / "LICENSE.md")
    for d in ("definitions", "examples"):
        if (out / d).exists():
            shutil.rmtree(out / d)
        shutil.copytree(js / d, out / d, ignore=shutil.ignore_patterns("__pycache__"))
    print(f"snapshot: {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    src = Path(args[args.index("--source") + 1]) if "--source" in args else ROOT / "source"
    sys.exit(main("--check" in args, src))
