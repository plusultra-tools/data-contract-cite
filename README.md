# data-contract-cite

**Add a verbatim regulatory citation layer to your open-data-contract-standard (ODCS) contracts.**

`data-contract-cite` reads an [ODCS](https://github.com/bitol-io/open-data-contract-standard)
contract and, for every field, emits a manifest that binds the field to the
specific article(s) of GDPR, HIPAA, EHDS and the EU Cyber Resilience Act (CRA)
that govern it — quoted verbatim, with article ID, official source URL, and a
SHA-256 chain so an auditor can prove the manifest has not drifted.

```bash
pip install data-contract-cite

dc-cite annotate \
  --contract contract.yaml \
  --regimes gdpr,hipaa \
  --output annotated/
```

That is the whole product. If you have an ODCS YAML/JSON contract and you ship
data in a regulated industry, the output of `dc-cite` is the artifact a DPO,
compliance officer or external auditor wants to see.

---

## Why this exists

Data engineers in healthcare, fintech and EU companies are converging on
**data contracts** (ODCS, dbt contracts, OpenMetadata schemas, Soda checks)
as the source of truth for what a dataset is, who owns it, what quality it
guarantees. The Bitol Foundation's
[open-data-contract-standard](https://github.com/bitol-io/open-data-contract-standard)
is rapidly becoming the de-facto YAML/JSON schema for this.

What ODCS does **not** do — and the broader data-quality tooling (Soda,
Great Expectations, Monte Carlo, OpenMetadata) also does not do — is tell you
**which regulation governs each field**. In a regulated industry that gap is
the entire conversation with your auditor:

> "You have `patient.medical_record_number` in this contract — under what
> regulation is it personal data, and where does that regulation say so?"

Today the answer lives in a separate Confluence page maintained by
compliance, drifts away from the contract within weeks, and is the first
thing a regulator picks apart.

`data-contract-cite` closes that gap by treating regulatory citations as a
**first-class artifact generated from the contract itself**, with the same
review/CI discipline as the contract.

---

## What it does

Given an ODCS contract like:

```yaml
# contract.yaml (ODCS v3)
apiVersion: v3.0.0
kind: DataContract
id: patient-records-v1
schema:
  - name: patient
    properties:
      - name: email
        logicalType: string
        physicalType: varchar(255)
        tags: [pii, contact]
      - name: medical_record_number
        logicalType: string
        physicalType: varchar(64)
        tags: [phi, identifier]
      - name: diagnosis_code
        logicalType: string
        physicalType: varchar(16)
        tags: [phi, health-data]
```

`dc-cite annotate --contract contract.yaml --regimes gdpr,hipaa` writes:

- `annotated/patient-records-v1.manifest.yaml` — per-field citation manifest
- `annotated/patient-records-v1.manifest.sha256` — content hash chain
- `annotated/patient-records-v1.contract.yaml` — original contract, untouched

A snippet of the manifest:

```yaml
contract_id: patient-records-v1
generator: data-contract-cite/0.1.0
fields:
  - path: patient.email
    citations:
      - regime: GDPR
        article: "Art. 4(1)"
        url: https://eur-lex.europa.eu/eli/reg/2016/679/oj
        verbatim: |
          'personal data' means any information relating to an identified
          or identifiable natural person ('data subject') ...
  - path: patient.medical_record_number
    citations:
      - regime: GDPR
        article: "Art. 4(1)"
        ...
      - regime: HIPAA
        article: "45 CFR §164.514(b)(2)(i)(H)"
        url: https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164
        verbatim: |
          Medical record numbers ... must be removed for de-identification
          under the Safe Harbor method.
  - path: patient.diagnosis_code
    citations:
      - regime: GDPR
        article: "Art. 9(1)"
        ...
        verbatim: |
          Processing of personal data revealing ... data concerning health
          ... shall be prohibited.
```

Three CLI subcommands:

| Command | Purpose |
|---------|---------|
| `dc-cite annotate` | Generate per-contract citation manifest. |
| `dc-cite validate` | Verify a manifest's SHA chain still matches its source contract. |
| `dc-cite manifest` | Dump the bundled citation-rules database (provenance audit). |

---

## Differentiator

| Tool | What it covers | Citation per field? |
|------|----------------|---------------------|
| **bitol-io/open-data-contract-standard** | Schema, quality, SLAs, ownership | No |
| **OpenMetadata** | Catalog, lineage, classification tags | No (free-text PII tag) |
| **Soda / Great Expectations** | Runtime quality checks | No |
| **Monte Carlo / Bigeye** | Observability, anomaly detection | No |
| **OneTrust / Collibra** | Enterprise GRC, policy mapping | Yes, but per-table and €€€ |
| **data-contract-cite** | **Per-field verbatim citation against GDPR / HIPAA / EHDS / CRA** | **Yes** |

The OSS data-contract / catalog ecosystem is schema- and quality-focused.
The commercial GRC ecosystem cites regulation but at policy-document
granularity and at enterprise pricing. Nothing in the middle gives a data
engineer a free, MIT-licensed, CI-runnable tool that binds **each contract
field** to the **verbatim regulatory clause** that makes that field a
regulated entity.

---

## Install

```bash
pip install data-contract-cite
dc-cite --version
```

Requires Python ≥ 3.10. Pure Python — `pyyaml` + `pydantic` only.

---

## Quickstart

```bash
pip install data-contract-cite

# 1. Annotate: generate the enriched contract + evidence pack
dc-cite annotate \
  --contract examples/quickstart/patient-events.contract.yaml \
  --annotations examples/quickstart/patient-events.annotations.yaml \
  --out output/

# 2. Verify the audit chain at any time
dc-cite validate output/audit.sha256

# 3. Dump the bundled citation database
dc-cite manifest
dc-cite manifest --json     # JSON format
```

See `examples/quickstart/` for a complete working example with expected outputs.

---

## CLI reference

```
dc-cite annotate --contract <path> --annotations <path> --out <dir/> [--allow-uncited]
dc-cite validate <audit.sha256>
dc-cite manifest [--json]
```

Exit codes: `0` success · `1` validation error (uncited PII / unknown regulation) ·
`2` usage error · `3` I/O error.

---

## Gap list (ODCS v3 fields not yet supported)

The following ODCS v3 fields are parsed by pydantic (`extra="allow"`) and
round-tripped faithfully through the enriched output, but `data-contract-cite`
does not generate or validate citations for them:

| ODCS v3 area | Status |
|---|---|
| `dataset.*` (datasetName, type, physicalDataset, priorContractId) | Pass-through only |
| `quality.*` (SLAs, checks, thresholds) | Pass-through only |
| `slaProperties`, `support`, `stakeholders`, `roles` | Pass-through only |
| `servers.*` (connection strings, environment definitions) | Pass-through only |
| `customProperties` | Pass-through only |
| `price`, `termsAndConditions` | Pass-through only |
| `tags[]` on schema objects (object-level, not field-level) | Not inspected |

Only field-level `pii: true` flags are used to gate citation requirements.
All other ODCS fields pass through `pydantic.model_config extra="allow"`.

PRs that add citation-gate logic for additional ODCS fields are welcome.

---

## Pricing

- **CLI / library:** MIT-licensed, free, forever.
- **Hosted CI (planned):** `dc-cite-ci` GitHub App that runs on every PR
  touching a contract, comments the diff of regulatory citations and blocks
  the merge if a field acquires a new regime without sign-off.
  €19/mo per repo, €49/mo for organizations. Stripe billing.

The free CLI is the whole product. Hosted CI exists for teams that don't
want to wire it into their own pipeline.

---

## Regimes covered (v0.1)

| Regime | Source | Coverage |
|--------|--------|----------|
| **GDPR** | Regulation (EU) 2016/679 | Art. 4(1), 4(13–15), 9(1), 32, 33, 35 |
| **HIPAA** | 45 CFR §164 | §164.514(b)(2) Safe Harbor identifiers, §164.312 technical safeguards |
| **EHDS** | Regulation (EU) 2025/327 | Arts. on electronic health data (placeholder, expands as final text stabilises) |
| **CRA** | Regulation (EU) 2024/2847 | Annex I essential cybersecurity requirements for products with digital elements |

The rule database is `src/data_contract_cite/data/citation_rules.yaml` — open
for PRs that add jurisdictions (UK GDPR, LGPD, CCPA, PIPEDA, APPI).

---

## Audit chain

Every manifest carries:

- `generator` — tool name and version that produced the manifest
- `source_sha256` — SHA-256 of the source ODCS contract
- `rules_sha256` — SHA-256 of `citation_rules.yaml` at generation time
- `manifest_sha256` — SHA-256 of the manifest body (excluding this field)

`dc-cite validate manifest.yaml --contract contract.yaml` recomputes all
three and exits 0 only if every hash matches. That single command is what
your CI runs to prove the manifest is current.

---

## Status

Alpha. v0.1 ships with ~15 rules covering the most common
PII/PHI/health-data field patterns. The bottleneck on coverage is regulatory
review of new rules, not engineering — PRs against `citation_rules.yaml`
that include the verbatim clause + source URL are the fastest path to
broader regime coverage.

This project is independent of and not endorsed by the Bitol Foundation.

---

## License

MIT. See `LICENSE`.
