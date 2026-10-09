# sdc_dcat3_us PRD: one SDC model, described in DCAT-US 3.0

**Status:** v0.3, 9 October 2026: **implemented; the NHANES Participant catalog passes GSA's validator at the pin and Data.gov's online validator** (section 6). The second projection demo of the projections track (ContentStrategy
lane 5.6, set 8 October): a public repository in the SemanticDataCharter org, one writer, the target's own validator
pinned by commit, one passing document from a published model on production, the README as the essay in four parts.
No issues are filed on the target's repositories (Tim, 9 October). The order of the track changes with this
repository: DCAT-US 3.0 is second, after CDIF; schema.org Dataset, DCAT-AP with HealthDCAT-AP and Croissant follow.

## 1. Facts

**What DCAT-US 3.0 is.** The United States federal data catalog metadata standard, the successor to DCAT-US v1.1
(the Project Open Data Metadata Schema of 2014, the `data.json` every agency publishes for Data.gov). It is an
application profile of the W3C Data Catalog Vocabulary version 3 (DCAT 3, W3C Recommendation 22 August 2024), not a
new standard, developed by the Federal Chief Data Officers Council, the Federal Committee on Statistical Methodology
and the Data.gov team at GSA, and governed by a CDO Tiger Team on a semi-annual cycle (spring and July releases; the
July release aligns with the OMB M-25-05 annual compliance date). Reference: https://resources.data.gov/resources/dcat-us3/
(page rewritten May and September 2026, with schema reference pages generated from the repository).

**Its shape.** Three tiers, as v1.1: a Catalog holds Datasets, each Dataset describes its Distributions. A `data.json`
file is a Catalog. The v3.0 schema is **JSON Schema 2020-12**, one definition file per class (26 classes: Catalog,
Dataset, Distribution, DataService, DatasetSeries, CatalogRecord, Agent, Organization, Kind (vCard contact), Address,
Identifier, Standard, Document, Concept, ConceptScheme, PeriodOfTime, Location, Checksum, Activity, Attribution,
Relationship, QualityMeasurement, Metric, AccessRestriction, UseRestriction, CUIRestriction). The earlier draft's RDF
form (a JSON-LD context and SHACL shapes from the DOI-DO repository) is kept under `DEPRECATED/` and is not the
validated form; the validated form is JSON against the JSON Schema. This is the first target whose validator is a
JSON Schema registry and not SHACL.

**Requirement levels** (from `requirementLevel` in the definitions at the pinned commit):
| Class | Mandatory | Recommended |
|---|---|---|
| Catalog | `dataset` | `conformsTo`, `issued`, `language`, `modified`, `rights`, `spatial`, `homepage`, `themeTaxonomy` |
| Dataset | `title`, `description`, `contactPoint` (a `Kind` with `fn` and `hasEmail`), `identifier` | `distribution`, `keyword`, `landingPage`, `theme`, `describedBy`, `inventoried`, `modified`, `publisher`, `license`, `accessRestriction`, `cuiRestriction`, `useRestriction`, `rights`, `spatial`, `temporal` |
| Distribution | none | `accessURL`, `describedBy`, `description`, `format`, `license`, `modified`, `rights`, `title`, the three restrictions |

Everything recommended accepts `null` ("Null allowed when not required"). `additionalProperties` is not set on the
classes, so an unknown property passes. Dates accept date-time, date, `YYYY` and `YYYY-MM`. `language` is a
two-letter ISO 639-1 code (a breaking change from v1.1's BCP 47). `identifier` is a string or an `Identifier` object
(`schemaAgency`, `notation`, `version`). `contactPoint` is one `Kind` or a list. `license` is a string (the crosswalk
says a URL to the legal document). `theme` entries are a string or a `Concept` object with `inScheme`.

**The statutory hook.** OMB Memorandum M-25-05 (Phase 2 implementation of the Evidence Act's open data title) lists
the metadata every agency's comprehensive data inventory must carry, and GSA publishes a crosswalk from each
requirement to a DCAT-US 3.0 property (https://resources.data.gov/resources/dcat-us-3-crosswalk/). Requirement **B,
"the names and definitions of all variables in the data asset," maps to `Dataset.describedBy`: "point to a
machine-readable feature catalog."** That is the slot a published SDC schema fills exactly: every variable with its
label, definition, datatype, units, enumerated values with their codes, and the sixteen typed reasons a value may be
missing. The other requirements map to `description`, `title`, `accessRights` with `rights` (open-data, FOIA and
Federal Data Catalog determinations), `mediaType` and `format` (open format), `license`, `rights` (Title 44
determinations), `inventoried`, `modified`, `accessURL` or `downloadURL`. Those determinations are an agency's, not
a model's; section 2 says how the writer treats them.

**Validation.** GSA's `jsonschema/test_json_schema.py` builds a `referencing` registry from `definitions/` (each
schema's `$id` is `https://resources.data.gov/dcat-us/3.0.0/definitions/<class>`, references are
`/dcat-us/3.0.0/definitions/<class>`) and validates with `Draft202012Validator` and the format checker; it runs their
`examples/<Class>/{good,bad}/` corpus and the examples embedded in the definitions, in CI on every pull request.
Data.gov also runs an online validator at https://harvest.data.gov/validate/. We use their script's method against
their definitions at the pin, offline, and the online validator by hand as the second witness.

**Sources, pinned 9 October 2026.** `github.com/GSA/dcat-us` at **4996591** (2026-10-07, "Merge pull request #180
from GSA/documentation-updates"), CC0 1.0 and 17 USC § 105 (a work of the United States Government). Cloned
read-only into `source/` (gitignored); `build/snapshot_dcat_us.py` verifies the pin and copies `jsonschema/definitions/`,
`jsonschema/test_json_schema.py`, `jsonschema/README.md` and `jsonschema/examples/` into `data/dcat-us-4996591/`. The
examples come too so the snapshot can prove itself intact by passing their own good and bad corpus. Re-pinning is a
deliberate step: bump the commit, re-run, record the result here. The W3C DCAT 3 Recommendation is cited, not copied.

**How DCAT-US relates to SDC: compose, not compete, as with CDIF, with a better-fitting seam.** DCAT-US describes a
data asset for a catalog and for the inventory the statute requires. SDC governs each record inside the asset. CDIF
had to be given the variables one by one (Data Description); DCAT-US asks for a pointer to the machine-readable
thing that defines them, and a published SDC schema is that thing, cited by URL and SHA-256.

## 2. Rules

**One deliverable: the writer.** From a published SDC model's package, a DCAT-US 3.0 Catalog (`data.json`) holding
one Dataset per model, validated with GSA's own JSON Schema at the pin. Later, a catalog of several models (the seven
FAIR Data Demo models) is the same writer run over a list.

**Two kinds of input, kept apart.**
1. **From the package** (nothing invented, as in `sdc_cdif`): title, description, identifier, publisher, dates,
   language, licence from the package's rights, keywords from the project, the schema's URL and SHA-256, the
   component count and the sixteen exceptional values for the description text.
2. **From the publisher of the catalog, declared** in a small `catalog.yaml` the writer reads and reports as declared
   input, because the schema makes them mandatory or the statute asks for them and the package cannot know them: the
   contact point (`fn`, `hasEmail`), the catalog's title and homepage, `accessRights` and any M-25-05 `rights`
   statements, `theme`. The README's part 3 says plainly which fields came from this file. For the sample, the
   publisher is Axius SDC, Inc., not an agency, so the M-25-05 determinations are left out and `accessRights` says
   `public` for the model.

**Mapping (the writer's rulebook):**
| SDC (package) | DCAT-US 3.0 |
|---|---|
| Published model, identifier `dm-<ct>` | `Dataset.identifier` as an `Identifier` object: `notation` `dm-<ct>`, `schemaAgency` the publisher; `@id` the public catalog URL |
| Title, description | `title`; `description` extended by one sentence saying what a governed data record is and that the schema is immutable and cited by SHA-256 |
| The published schema `/dmlib/dm-<ct>.xsd?sha256=` | **`describedBy`**: a `Distribution` (`title`, `downloadURL` the pinned URL, `mediaType` `application/xml`, `format` `XSD`, `checksum` with `sha256`, `modified`); **and** `conformsTo`: a `Standard` (`identifier` the same URL, `title`, `modified`) |
| The SDC4 reference model | `describedBy.conformsTo`: a `Standard` for `https://semanticdatacharter.com/ns/sdc4/sdc4.xsd` |
| Model date | `modified`, `issued`; `inventoried` = the day the catalog was written |
| `dc:language` `en-US` | `language` `en` (two letters, as the schema requires) |
| `dc:rights` with a URL | `license` (the URL, as the crosswalk asks) |
| `dc:creator` | `creator` (an `Agent` with `name`) |
| Publisher link | `publisher` (an `Organization` with `name`, `@id`) |
| Public catalog URL | `landingPage` (a `Document` with `title`, `accessURL`) |
| Project name, "Semantic Data Charter", "governed data record" | `keyword` |
| Immutability | `versionNotes` or `provenance` text: a published model never changes; a revision is a new model naming the one it revised. (`publishingPrinciples` has no DCAT-US slot.) |
| The records themselves | `distribution`: omitted for the sample (the records are not public; the schema allows omission "when no distribution is available yet") and stated in part 3; present when a publisher has a download or access URL |
| Declared input | `contactPoint`, catalog `title`/`homepage`/`description`, `accessRights`, `rights`, `theme` |

**Not here.** The RDF form (deprecated by GSA); DCAT-AP and HealthDCAT-AP (their own repository, their own SHACL);
geospatial, dataset series, data services, quality measurements (no source in the package); converting v1.1
catalogs (GSA ships that).

**Attribution.** CC0 sources, but credited: a NOTICE naming GSA, the Data.gov program and the CDO Tiger Team, and the
pinned commit in `data/`.

**No issues filed** on `GSA/dcat-us` (Tim, 9 October). Part 4 carries how the artifacts behave, inside their scope,
not defects. Held privately, not for the README: the overview page says `bureauCode` and `programCode` "are all
still present and recognized in v3.0," and the definitions at the pin carry neither property (an unknown property
passes because `additionalProperties` is unset, so an agency's values would be accepted and unchecked).

## 3. Scope

### 3.1 First: one model, the same record as `sdc_cdif`
- NHANES Participant (`xy8upneajsb8vdcmnve01g6g`, FAIR Data Demo), the same package fetched from production, so the
  capstone's matrix has the same record in every row.
- A `data.json` Catalog with one Dataset, passing GSA's validator against `Catalog` and the Dataset against
  `Dataset` at the pin, 0 errors; the snapshot proven intact by their own good and bad corpus; the online validator
  as the second witness, by hand, recorded in the README.
- The README in the four parts.

### 3.2 Then: a catalog
The seven FAIR Data Demo models as one `data.json`, one command. The federal-data lane's demonstration: a
comprehensive data inventory entry per governed model, with requirement B satisfied by the schema.

### 3.3 Later
- Any published model (`--ct-id`), as in `sdc_cdif`.
- `distribution` entries when a publisher exposes records (a CordovaOS domain with an access URL).
- SDCStudio "Download data.json" as a thin call into the package, if wanted.

## 4. Decisions (proposed; open for Tim)
1. **Package name `sdcdcatus`**, repository `sdc_dcat3_us`, the `sdc_cdif` layout (`src/`, `data/`, `samples/`,
   `tests/`, `build/`, NOTICE, CI, dev to main by pull request with merge commits).
2. **The package loader and model reader are copied from `sdccdif`**, not shared yet: lane 5.6 says shared code when
   the third repository repeats the second. The third (schema.org) will be the moment to lift them into one package.
3. **The contact point is declared input, with a configurable default.** DECIDED 9 October (Tim). The schema makes
   `contactPoint` with an e-mail mandatory and the package has none. The address lives in the declared-input file
   beside the contact's name, never in code; the package ships a default file carrying **`contact@axius-sdc.com`**
   and the name "Axius SDC, Inc. DCAT contact" (the name names the repository, so incoming mail filters by it; the CDIF repository uses "Axius SDC, Inc. CDIF contact"), overridable by editing the file or by `--contact-email` and
   `--contact-name`. The writer refuses an empty address rather than inventing one. `noreply@` was considered and
   rejected: the field is a vCard address people use to ask questions, and an address that will not read mail says
   the opposite of what the field means. The mailbox exists before the sample is published. When the default has to
   change, it is one line in one file and a re-run.
4. **The schema fills both `describedBy` and `conformsTo`.** Two roles, one URL: the data dictionary the statute asks
   for, and the standard the records conform to.
5. **No `distribution` on the sample**, stated in part 3, because the FAIR demo's records are not published; the
   writer emits one when the declared input gives a URL.
6. **The M-25-05 determinations are an agency's**, taken as declared input and never defaulted. The sample carries
   `accessRights: public` for the model and no determinations.
7. **Second witness by hand.** The online validator at harvest.data.gov is run once on the sample and its result
   recorded in the README with the date; it is not in CI.

## 5. Pipeline
`source/` (GSA/dcat-us at 4996591, read-only), then `build/snapshot_dcat_us.py` (verify the pin; copy definitions,
script, README and examples to `data/dcat-us-4996591/`), then `src/sdcdcatus/` (`package.py` and `model.py` from
`sdccdif`; `dcatus.py` emits the Catalog; `cli.py`: `sdcdcatus write --package DIR --catalog catalog.yaml [--out
data.json]`), then `tests/` (their registry and validator against our output; their corpus against the snapshot),
then the README. CI on pull requests and main, offline.

## 6. Results, 9 October 2026

- `samples/nhanes-participant/data.json`: a Catalog with one Dataset, written from the package fetched from production
  (schema SHA-256 `0df45878...3b3b`, the published current version).
- GSA's method at 4996591 (registry of the 26 definitions, `Draft202012Validator`, format checker): Catalog, Dataset
  and the `describedBy` Distribution, **0 errors**. Their own corpus on the snapshot: 510 pass, 0 fail.
- Data.gov's online validator (https://harvest.data.gov/validate/, "dcatus3.0 catalog", pasted): **"No validation
  errors found."**
- 7 tests in `tests/`, under a second. CI offline.
- Decisions 1 to 7 implemented as written; decision 3's default address and name ship in
  `src/sdcdcatus/data/catalog.yaml`. One addition while building: the format extras (`jsonschema[format]`) are
  required for the tests, because without them format assertions pass silently; recorded in the README's part 4.
- **Section 3.2 done, 9 October (Tim: "run the seven FAIR demo models as one data.json"):**
  `samples/fair-data-demo/data.json`, seven Datasets from the packages fetched from production and saved beside it;
  GSA's schema at the pin, 0 errors; Data.gov's online validator, "No validation errors found"; a test re-runs the
  writer over the saved packages and asserts the committed file equal. Found on the way: the catalog's artifact
  endpoint answers with a storage pointer (`download_url`) for the JSON-LD, which `fetch_package` now follows (fixed
  in `sdc_cdif` too).
- 10 October note for the record: the writers read the model's Dublin Core from the schema header (Tim, 9 October),
  with SDCStudio's defaults as unset; SDCStudio issues #748 and #749 filed for the package's metadata gaps.
