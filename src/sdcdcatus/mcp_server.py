#
# Copyright (c) 2026, Axius SDC, Inc.
# Licensed under the Apache License, Version 2.0.
#
"""
MCP stdio server for `sdcdcatus`: one tool, `write_catalog`, over the same function the CLI calls.

An agent that can read a published model with `sdcreader` can ask this server for its DCAT-US 3.0 description.
The scaffold (JSON-RPC over stdio, protocol negotiation, `isError` results, the package cache) is `sdcreader.mcp`,
shared by every SDC projection server. No tool takes a URL: the catalog host is fixed at start with `--host`.
"""

from __future__ import annotations

import json
from datetime import date
from typing import Any

from sdcreader.mcp import PackageCache, Server, ToolError, source_properties, str_arg
from sdcreader.package import DEFAULT_HOST, fetch_package  # noqa: F401  (patched by tests)

from sdcdcatus import __version__
from sdcdcatus.dcatus import DeclaredInputError, load_declared, write_catalog

SERVER_NAME = "sdcdcatus"
ISSUES = "https://github.com/SemanticDataCharter/sdc_dcat3_us/issues"

_HOST: str = DEFAULT_HOST
_CACHE: dict = {}

TOOLS = [
    {
        "name": "write_catalog",
        "description": (
            "Write a DCAT-US 3.0 catalog (data.json) describing one or more published Semantic Data Charter models as datasets, each with the model's schema cited as describedBy (the data dictionary) and conformsTo by URL and SHA-256. A contact name and e-mail are mandatory in DCAT-US; the package's defaults apply unless given. Validated in this package's CI with GSA's own JSON Schema at a pinned commit."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                **source_properties(plural=True),
                "contact_name": {"type": "string", "description": "The publisher's contact point name; the package's declared default applies when omitted."},
                "contact_email": {"type": "string", "description": "The publisher's contact e-mail; the package's declared default applies when omitted."},
                "date": {"type": "string", "description": "The catalog date, YYYY-MM-DD; today when omitted."}
            },
            "additionalProperties": False,
        },
    },
]


def _cache() -> PackageCache:
    import sdcdcatus.mcp_server as me

    return PackageCache(host=_HOST, storage=_CACHE, fetcher=lambda ct_id, host: me.fetch_package(ct_id, host=host))


def _date(args: dict[str, Any]) -> date | None:
    v = str_arg(args, "date")
    if v is None:
        return None
    try:
        return date.fromisoformat(v)
    except ValueError as exc:
        raise ToolError("`date` must be YYYY-MM-DD.") from exc


def _format(args: dict[str, Any]) -> str:
    fmt = str_arg(args, "format", "turtle")
    if fmt not in ("turtle", "json-ld"):
        raise ToolError("`format` must be turtle or json-ld.")
    return fmt


def _handle_write(args: dict[str, Any]) -> Any:
    items = _cache().many(args)
    today = _date(args)
    try:
        declared = load_declared(None, str_arg(args, "contact_name"), str_arg(args, "contact_email"))
    except DeclaredInputError as exc:
        raise ToolError(str(exc)) from exc
    catalog = write_catalog([m for _, m in items], declared, today=today)
    return {
        "standard": "DCAT-US 3.0", "datasets": len(catalog["dataset"]),
        "models": [{"ct_id": m.ct_id, "title": m.title, "schema_url_pinned": p.schema_url_pinned} for p, m in items],
        "document": catalog,
        "note": "Validated in this package's CI against GSA's DCAT-US 3.0 JSON Schema at a pinned commit; the schema is not shipped in the wheel.",
    }


TOOL_HANDLERS = {"write_catalog": _handle_write}


def _server() -> Server:
    return Server(
        name=SERVER_NAME, version=__version__, tools=TOOLS, handlers=TOOL_HANDLERS, issues_url=ISSUES,
        instructions=(
            "Describe published Semantic Data Charter models in DCAT-US 3.0 terms. `write_catalog` takes "
            + ("model identifiers (ct_ids), fetched from " if True else "a model identifier (ct_id), fetched from ")
            + f"{_HOST}, or package directories on disk, and returns the data.json catalog under `document`. "
            "Read-only apart from the document it returns; no account; no tool takes a URL."
        ),
    )


def _handle_request(request: Any) -> dict | None:
    return _server().handle(request)


def main(argv: list[str] | None = None) -> None:
    """Entry point for `sdcdcatus-mcp` and `sdcdcatus mcp`."""
    import argparse

    global _HOST

    parser = argparse.ArgumentParser(prog="sdcdcatus-mcp", description="MCP stdio server: DCAT-US 3.0 descriptions of published Semantic Data Charter models.")
    parser.add_argument("--host", default=DEFAULT_HOST,
                        help=f"The SDCStudio host whose public catalog is read, fixed here so a caller cannot redirect the server. Default {DEFAULT_HOST}.")
    args = parser.parse_args(argv)
    _HOST = args.host.rstrip("/")
    _server().run_stdio()


if __name__ == "__main__":
    main()
