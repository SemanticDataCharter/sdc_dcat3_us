# Pinned snapshot

Copied 9 October 2026 from `GSA/dcat-us` at commit 4996591 (2026-10-07; CC0 1.0 and 17 USC § 105, a work of the United
States Government): `jsonschema/definitions/` (the 26 class schemas), `jsonschema/examples/` (their good and bad
corpus), `jsonschema/test_json_schema.py` (their validator) and `jsonschema/README.md`. The writer's tests validate
against these, so a passing catalog records which DCAT-US it passed, and run their corpus to prove the snapshot is
intact. Re-pinning is a deliberate step: bump the commit in `build/snapshot_dcat_us.py`, re-run, record the result in
the PRD.
