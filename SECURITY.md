# Security policy

## Supported versions

The latest released version is supported.

## Reporting a vulnerability

Please email `plusultra.dev@proton.me` (preferred) with a description of the issue
and reproduction steps. Do not file public GitHub issues for security reports.

We aim to acknowledge within 7 days and to publish a fix or mitigation within
30 days for confirmed vulnerabilities. For coordinated disclosure timelines,
please indicate any embargo you require.

## Data-handling note

This tool processes ODCS YAML contracts that may contain field-level PII
classifications and regulatory annotations. The CLI never transmits data over
the network. All output artifacts (enriched YAML, evidence JSON, audit SHA-256)
are written to the local filesystem only. The bundled citation-map
(`data/citation_map.yaml`) contains only public regulatory text and URLs —
no personal or confidential data.

Operators are responsible for ensuring that any ODCS contract YAML passed to
`dc-cite` does not itself contain row-level personal data (e.g., sample values
in `examples:` blocks). The tool processes schema metadata, not data records.
