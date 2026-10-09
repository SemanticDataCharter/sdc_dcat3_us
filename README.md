# sdc_dcat3_us

One Semantic Data Charter model, described in DCAT-US 3.0.

`sdcdcatus` reads a published SDC model's package and writes the `data.json` Catalog that DCAT-US 3.0, the United
States federal data catalog standard, asks an agency to publish: one Dataset per model, with the model's schema cited
as the data dictionary (`describedBy`) and as the standard the records conform to (`conformsTo`), by URL and SHA-256.
The output is checked with GSA's own JSON Schema and validation script at a pinned commit of `GSA/dcat-us`, and with
Data.gov's online validator.

## 1. What this is, and where it came from

The sample, `samples/nhanes-participant/data.json`, is a Catalog with one Dataset: the records of **NHANES
Participant** (`dm-xy8upneajsb8vdcmnve01g6g`) from the FAIR Data Demo, a demographic, examination and laboratory
record of the National Health and Nutrition Examination Survey (CDC). The model is public:

- the catalog record: https://sdcstudio.axius-sdc.com/api/v1/catalog/dm/xy8upneajsb8vdcmnve01g6g/
- the schema the records conform to: https://sdcstudio.axius-sdc.com/dmlib/dm-xy8upneajsb8vdcmnve01g6g.xsd
- the Semantic Data Charter: https://semanticdatacharter.com

```
pip install -e ".[fetch]"
sdcdcatus write --package samples/nhanes-participant --out data.json
sdcdcatus write --ct-id xy8upneajsb8vdcmnve01g6g --ct-id <another> --save-package pkg/ --out data.json   # a catalog of models, from the public catalog
sdcdcatus write --package DIR --catalog my-catalog.yaml --contact-email data@agency.gov --out data.json  # a publisher's own declared input
```

**Two kinds of input, kept apart.** From the model's package (its JSON-LD, its schema, the public catalog record and
the published schema versions; no account needed; a model without a package is refused): title, description,
identifier, publisher, dates, language, licence, the schema's URL and SHA-256, the variable count. From the catalog's
publisher, declared in `catalog.yaml` because the schema or the statute asks for it and the package cannot know it:
the contact point, the catalog's own title, description and homepage, and what the publisher asserts about access.
The package ships a default file for the sample (`src/sdcdcatus/data/catalog.yaml`); an agency supplies its own.

**Why `describedBy`.** OMB Memorandum M-25-05 requires every agency's comprehensive data inventory to carry "the names
and definitions of all variables in the data asset," and GSA's crosswalk maps that requirement to `describedBy`: a
Distribution pointing at a machine-readable data dictionary. A published SDC schema is that: every variable with its
label, definition, datatype, units, permitted values with their codes, and the sixteen typed reasons a value may be
missing, immutable once published and cited here by URL and SHA-256.

What the Dataset carries:

| | |
|---|---|
| `title`, `description` | the model's, plus one sentence saying what a governed data record is and that the schema is the data dictionary |
| `identifier` | an `Identifier`: `notation` `dm-xy8upneajsb8vdcmnve01g6g`, `schemaAgency` the publisher |
| `contactPoint` | a `Kind` with `fn` and `hasEmail`, from the declared input |
| `publisher`, `creator`, `landingPage`, `keyword`, `license`, `language` `en` | from the package |
| `describedBy` | a `Distribution`: the schema's pinned URL as `downloadURL`, `application/xml`, `XSD`, a SHA-256 `Checksum`, `conformsTo` the SDC4 reference model |
| `conformsTo` | a `Standard` for the same pinned URL |
| `issued`, `modified` | the model's publication date; `inventoried` the day the catalog was written |
| `accessRights` | `public`, as the publisher declares for the model |
| `versionNotes` | a published model never changes; a revision is a new model naming the one it revised; the SHA-256 and the permanence page |

## 2. How to verify it

The tests run GSA's own validator from `data/dcat-us-4996591/`, where their 26 class definitions, their example corpus
and their `test_json_schema.py` are copied at the pinned commit (`build/snapshot_dcat_us.py` verifies the pin first):

```
pip install -e ".[dev]"
python -m pytest tests -q
```

The suite first runs their script on the snapshot (their good and bad corpus: 510 pass, 0 fail at the pin), then
validates the sample Catalog, its Dataset and the `describedBy` Distribution with their method, a `referencing`
registry of every definition by `$id` and `Draft202012Validator` with the format checker: 0 errors.

Second witness, Data.gov's online validator at https://harvest.data.gov/validate/ (schema "dcatus3.0 catalog", paste
or upload the sample): **"No validation errors found"**, 9 October 2026.

## 3. What the projection could not say

Left out rather than filled in:
- **No `distribution` of the records.** The FAIR Data Demo's records are not published; the model is. The schema
  allows a Dataset without distributions, and the writer emits them when a publisher declares an access or download
  URL.
- **Nothing an agency would have to determine.** The M-25-05 open-data, FOIA, Federal Data Catalog, open-format and
  licensing determinations, the Title 44 statements, the access, use and CUI restrictions, bureau and program codes:
  all of these are an agency's assertions. The writer takes them only as declared input and defaults none of them.
  The sample, published by a company and not an agency, carries `accessRights: public` and no determinations.
- **No spatial or temporal coverage, no theme, no quality measurements.** The package does not carry them.

Declared rather than read from the package, and said so here: the contact point (`contact@axius-sdc.com` on the
sample), the catalog's title, description and homepage, the publisher's name and identifier, `accessRights`.

In the other direction, what the record carries that a catalog entry has no place for, stated so a reader knows
where to look rather than as a shortcoming of either side:
- **The governance envelope is data in every record.** Each Governed Data Record carries its own audit event, PROV
  activity and PROV agent as validated leaves. DCAT-US's `provenance`, `wasGeneratedBy` and `qualifiedAttribution`
  describe the dataset; the per-record facts are in the records, defined in the data dictionary.
- **The schema is bound to each record.** Every record names the schema it was validated against; the catalog can
  say that once, which `conformsTo` with the SHA-256 does.
- **The reason a value is missing is typed in the record.** A leaf may carry one of sixteen exceptional values in
  place of its value; the data dictionary defines them; which one applies, and where, is in the record.

## 4. What we learned about DCAT-US 3.0

Implementer's notes from building this against `GSA/dcat-us` at 4996591. They describe how the artifacts behave, so
the next implementer spends the day on their own catalog rather than on these.

- **The validated form is JSON against JSON Schema 2020-12.** The earlier draft's JSON-LD context and SHACL shapes
  (from the Interior Department's repository) sit under `DEPRECATED/`; a `data.json` is what the script and the
  online validator check. An implementer coming from DCAT-AP, which is SHACL over RDF, should not look for shapes.
- **Format assertions need the extras.** The definitions use `format: date`, `date-time` and `iri`. With plain
  `jsonschema` those are not checked, and six of GSA's own "bad" examples pass; with `jsonschema[format]`, which
  their CI installs, all 510 corpus cases behave as labelled. The tests here require the extras.
- **Unknown properties pass.** `additionalProperties` is not set on the classes, so a misspelled or legacy property
  is accepted without a message. The validator tells you what is missing or malformed, not what it did not recognize.
- **Null means "not provided."** Every recommended property accepts `null` explicitly ("Null allowed when not
  required"); omitting the property is equally valid.
- **`language` is two letters** (ISO 639-1), a documented breaking change from v1.1's BCP 47; `en-US` fails.
- **Dates take four forms:** date-time, date, `YYYY`, `YYYY-MM`.
- **`identifier` is a string or an `Identifier` object** (`notation`, `schemaAgency`, `version`); `contactPoint` is
  one `Kind` or a list; `hasEmail` must match a `mailto:` pattern; `license` is a string (the crosswalk says a URL).
- **`describedBy` is a `Distribution`, not a `Document`**, so a data dictionary gets a `downloadURL`, a `mediaType`,
  a `checksum` and its own `conformsTo`. That is the right shape for a schema.
- **`conformsTo` is a single `Standard` on a Catalog and a list of them on a Dataset.** Both accept
  `identifier` as a string or an `Identifier` object.
- **A Distribution has no mandatory property**, and a Dataset has four: `title`, `description`, `contactPoint`,
  `identifier`. Everything else that the statute asks for is Recommended.
- **The registry method.** Each definition's `$id` is `https://resources.data.gov/dcat-us/3.0.0/definitions/<class>`
  and references are the path `/dcat-us/3.0.0/definitions/<class>`; a `referencing` registry built from the directory
  resolves them, as `test_json_schema.py` does. The online validator agreed with the script on the sample.

## Layout

- `src/sdcdcatus/`: `package.py` and `model.py` (reused from `sdc_cdif`: a model's package, from a directory or the
  public catalog, and its record tree), `dcatus.py` (the Catalog), `cli.py`, `data/catalog.yaml` (the declared input
  for the sample).
- `data/dcat-us-4996591/`: GSA's definitions, examples, validator and README at the pin.
- `samples/nhanes-participant/`: the model's package as fetched and the `data.json` written from it.
- `build/snapshot_dcat_us.py`: re-creates `data/` from a read-only clone of `GSA/dcat-us` at the pinned commit.

## Licences

Apache-2.0 (see `LICENSE`, `NOTICE`). The DCAT-US artifacts in `data/` are a work of the United States Government
(17 USC § 105) released under CC0 1.0 and keep that status here.
