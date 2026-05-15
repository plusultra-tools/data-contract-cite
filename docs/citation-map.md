# Supported regulations and articles

This table lists all entries in the bundled citation map
(`src/data_contract_cite/data/citation_map.yaml`).

For custom jurisdictions, add entries to `citation_map.yaml` and submit a PR.
Fields using custom regulations MUST set `excerpt_type: paraphrase` unless the
regulation appears in the bundled map.

---

## GDPR — Regulation (EU) 2016/679

| Article | Title | Excerpt type | Source |
|---|---|---|---|
| Art. 4(1) | Definition of personal data | verbatim_oj | [EUR-Lex OJ](https://eur-lex.europa.eu/eli/reg/2016/679/oj) |
| Art. 4(13) | Definition of genetic data | verbatim_oj | [EUR-Lex OJ](https://eur-lex.europa.eu/eli/reg/2016/679/oj) |
| Art. 4(14) | Definition of biometric data | verbatim_oj | [EUR-Lex OJ](https://eur-lex.europa.eu/eli/reg/2016/679/oj) |
| Art. 4(15) | Definition of data concerning health | verbatim_oj | [EUR-Lex OJ](https://eur-lex.europa.eu/eli/reg/2016/679/oj) |
| Art. 9(1) | Processing of special categories — prohibition | verbatim_oj | [EUR-Lex OJ](https://eur-lex.europa.eu/eli/reg/2016/679/oj) |
| Art. 32 | Security of processing | verbatim_oj | [EUR-Lex OJ](https://eur-lex.europa.eu/eli/reg/2016/679/oj) |
| Art. 33 | Notification of personal data breach | verbatim_oj | [EUR-Lex OJ](https://eur-lex.europa.eu/eli/reg/2016/679/oj) |
| Art. 35 | Data protection impact assessment | verbatim_oj | [EUR-Lex OJ](https://eur-lex.europa.eu/eli/reg/2016/679/oj) |

---

## HIPAA — 45 CFR §164

| Article | Title | Excerpt type | Source |
|---|---|---|---|
| 45 CFR §164.514(b)(2)(i) | Safe Harbor de-identification — 18 identifiers to remove | verbatim_cfr | [eCFR §164.514](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-E/section-164.514) |
| 45 CFR §164.312(a) | Technical safeguards — access control | verbatim_cfr | [eCFR §164.312](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-C/section-164.312) |

---

## EHDS — Regulation (EU) 2025/327

| Article | Title | Excerpt type | Source |
|---|---|---|---|
| Art. 64-72 | Secondary use of electronic health data | paraphrase | [EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32025R0327) |

Note: EHDS verbatim text will be added as the final consolidated OJ text stabilises.

---

## CRA — Regulation (EU) 2024/2847

| Article | Title | Excerpt type | Source |
|---|---|---|---|
| Annex I, Part I | Essential cybersecurity requirements | paraphrase | [EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R2847) |
| Art. 14 | Vulnerability handling obligations of manufacturers | paraphrase | [EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R2847) |

---

## Adding a new regulation

1. Add entries to `src/data_contract_cite/data/citation_map.yaml`.
2. Each entry requires: `regulation`, `article`, `title`, `excerpt`, `excerpt_type`,
   `source_url`, `tags`.
3. For verbatim EU OJ text: use `excerpt_type: verbatim_oj`.
4. For verbatim US CFR text: use `excerpt_type: verbatim_cfr`.
5. For paraphrase (non-verbatim or not-yet-consolidated text): use `excerpt_type: paraphrase`.
6. Open a PR with the verbatim source + URL. The project maintainer will review for accuracy.

Jurisdictions on the roadmap: UK GDPR, LGPD (Brazil), CCPA (California), PIPEDA (Canada), APPI (Japan).
