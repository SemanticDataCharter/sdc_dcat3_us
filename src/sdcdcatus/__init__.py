"""Describe a published Semantic Data Charter model's governed data records in DCAT-US 3.0.

One or more models in, one data.json Catalog out: a Dataset per model, its schema cited as the data dictionary
(describedBy) and the standard the records conform to (conformsTo), by URL and SHA-256. Validated with GSA's own JSON
Schema at a pinned commit.
"""
from sdcreader import ModelPackage, load_package, fetch_package, read_model
from .dcatus import write_catalog, load_declared, DeclaredInputError

__version__ = "4.0.0"
__all__ = ["ModelPackage", "load_package", "fetch_package", "read_model", "write_catalog", "load_declared", "DeclaredInputError", "__version__"]
