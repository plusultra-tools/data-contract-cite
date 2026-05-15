# Landing copy -- data-contract-cite

For the future Carrd / static landing page.

---

## Hero

**Regulatory citations, first-class in your data contracts.**

A free CLI that binds every PII field in your ODCS data contract to the
verbatim GDPR / HIPAA / EHDS / CRA clause that governs it — hash-chained, CI-runnable,
auditor-ready. MIT-licensed. Runs on your machine.

[GitHub](https://github.com/plusultra-tools/data-contract-cite) --
[PyPI](https://pypi.org/project/data-contract-cite/) --
[Docs](https://github.com/plusultra-tools/data-contract-cite/blob/main/README.md)

---

## What it does

Feed it an ODCS contract and an annotations file. Get a compliance evidence pack out:

- An enriched contract YAML with `regulatory_citations:` per field.
- A machine-readable `dc_evidence.json` manifest: field × regulation × article × verbatim excerpt + source URL.
- A human-readable `dc_evidence.md` rendering.
- An `audit.sha256` hash chain so your CI can prove the manifest is current.

One command:

```bash
dc-cite annotate \
  --contract contract.yaml \
  --annotations annotations.yaml \
  --out output/
```

---

## Why this exists

Data engineers at EU healthcare companies, fintechs, and large-platform teams
are converging on ODCS contracts as the authoritative description of a dataset.
The ODCS schema tells auditors what a field is. It does not tell them *which
regulation governs that field and what the regulation says*.

That gap — always filled by a drifting Confluence page — is the first thing
a DPO or external auditor picks apart.

`data-contract-cite` closes the gap by making regulatory citations a
version-controlled artifact with the same CI discipline as the contract itself.

---

## For who

- Data engineers at EU healthcare / fintech companies building ODCS-governed data products.
- Compliance / DPO teams who need a traceable, reproducible citation artifact.
- Platform teams running ODCS contracts in CI and wanting to gate on regulatory coverage.
- External auditors who want a structured evidence pack instead of a free-text annex.

---

## Regulations covered (v0.1)

| Regulation | Coverage |
|---|---|
| GDPR | Art. 4(1) personal data definition, Art. 9(1) special-category prohibition, Art. 32-35 security / DPIA |
| HIPAA | 45 CFR §164.514(b)(2) Safe Harbor identifiers (18 verbatim) |
| EHDS | Arts. 64-72 electronic health data (paraphrase + OJ URL) |
| CRA | Annex I essential cybersecurity requirements (paraphrase + OJ URL) |

Open for PRs that add UK GDPR, LGPD, CCPA, PIPEDA, APPI.

---

## Pricing

- **CLI / library:** MIT-licensed, free, forever.
- **Hosted CI (planned):** `dc-cite-ci` GitHub App that runs on every PR
  touching a contract file, comments the regulatory-citation diff, and blocks
  the merge if a PII field acquires a new regime without sign-off.
  €19/mo per repo, €49/mo for organisations.

---

## Reserve early access

Form below — email + role + organisation. No tracking, no selling, one-click unsubscribe.

(Form embed)

---

## Why us

Built out of frustration with the ODCS → DPO handoff at a Spanish healthtech.
Not a consultancy product, not an enterprise GRC bolt-on: a free tool that
data engineers actually run in CI.
