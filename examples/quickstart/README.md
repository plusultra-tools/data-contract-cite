# Quickstart example

This directory contains a minimal example of `dc-cite annotate`.

## Files

- `patient-events.contract.yaml` — synthetic ODCS v3 contract with PII fields.
- `patient-events.annotations.yaml` — annotations mapping each PII field to
  GDPR, HIPAA, and EHDS citations.

## Run

```bash
pip install data-contract-cite

dc-cite annotate \
  --contract patient-events.contract.yaml \
  --annotations patient-events.annotations.yaml \
  --out out/
```

## Expected outputs

```
out/
├── patient-events-quickstart-enriched.yaml   # contract + regulatory_citations per field
├── dc_evidence.json                          # machine-readable manifest
├── dc_evidence.md                            # human-readable rendering
└── audit.sha256                              # SHA-256 chain over all artifacts
```

## Verify the audit chain

```bash
dc-cite validate out/audit.sha256
# OK: all hashes match — manifest is current.
```

## Output snippet (enriched YAML)

```yaml
schema:
  - name: patient
    properties:
      - name: email
        pii: true
        regulatory_citations:
          - regulation: GDPR
            article: Art. 4(1)
            excerpt: "'personal data' means any information relating to..."
            excerpt_type: verbatim_oj
            source_url: https://eur-lex.europa.eu/eli/reg/2016/679/oj
          - regulation: HIPAA
            article: 45 CFR §164.514(b)(2)(i)
            excerpt: Electronic mail addresses must be removed...
            excerpt_type: paraphrase
```
