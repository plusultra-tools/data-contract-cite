# Changelog

All notable changes to this project will be documented here.

## v0.1.0 -- 2026-05-15 (initial release)

- CLI `dc-cite` with three subcommands: `annotate`, `validate`, `manifest`.
- Pydantic v2 models for ODCS v3 contract subset (id, kind, status, version,
  schema fields with pii flag, logicalType, physicalType, classification).
- Annotations YAML model: per-field list of {regulation, article, excerpt,
  excerpt_type, source_url}.
- Bundled citation map covering GDPR Art. 4(1), 9(1), 32, 33, 35; HIPAA 45 CFR
  §164.514(b)(2) Safe Harbor identifiers; EHDS Arts. 64-72 (paraphrase + OJ
  URL); CRA Annex I essential requirements (paraphrase + OJ URL).
- Validator: enforces that every `pii: true` field has at least one annotation;
  exits non-zero unless `--allow-uncited` flag is set.
- Enricher: merges contract + annotations → enriched YAML with
  `regulatory_citations:` block per field.
- Evidence builder: per-field manifest JSON with verbatim excerpts, source URLs,
  timestamps.
- SHA-256 audit chain over contract + annotation + enriched output + evidence.
- `dc-cite validate` recomputes hash chain and exits 0 only on full match.
- `dc-cite manifest` dumps bundled citation-rules database.
- 46 pytest cases passing under Python 3.10/3.11/3.12.
- Example quickstart: synthetic patient-events contract + annotations.
- `docs/citation-map.md`: table of all supported regulations and articles.

## Roadmap (v0.2 candidates, dependent on signal)

- Auto-discovery mode: infer likely regulations from field name heuristics
  (e.g., `email`, `ssn`, `dob`).
- UK GDPR, LGPD, CCPA, PIPEDA, APPI coverage.
- Hosted CI GitHub App: validates every PR touching a contract file.
- JSON output format in addition to YAML.
- dbt contract and OpenMetadata schema input adapters.
