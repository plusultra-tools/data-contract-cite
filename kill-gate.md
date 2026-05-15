# Kill-gate -- data-contract-cite

**Set:** 2026-05-15.
**Day-0 = day of GitHub-release / PyPI publication.**
**Decision day = Day-30.** Secondary gate at d+60 for commercial inquiries.

---

## Pass conditions (any ONE = continue to Phase 2 / hosted CI)

| Metric | Threshold | How measured |
|---|---|---|
| GitHub stars | ≥ 30 by d+30 | Public counter on repo |
| `pip install data-contract-cite` per pypistats `last_week` | ≥ 10 by d+30 | https://pypistats.org |
| Real-affiliation issues (data-engineering / compliance team) | ≥ 2 by d+30 | GitHub profile bio + employer |
| Inbound data-engineering team (≥3 people) integrating the tool | ≥ 1 by d+30 | Email / GitHub discussion |
| Commercial inquiry (hosted CI / consulting) | ≥ 1 by d+60 | Email plusultra.dev@proton.me |

**Hitting any one = green.**

---

## Fail conditions (ALL of the below => kill)

- < 5 stars by d+30
- 0 real-affiliation issues by d+30
- 0 inbound commercial / integration emails by d+60
- 0 PyPI installs last_week at d+30

If all hit, archive repo, post-mortem, retain code for portfolio.

---

## Yellow zone

1 metric near threshold, others well below: publish one technical post on
`dev.to` or the ODCS GitHub Discussions explaining the compliance gap the tool
closes. Cross-post to data-engineering subreddits and data-mesh Slack
communities. Wait additional 30d. Re-evaluate at d+90.

---

## Phase 2 conditions

On green pass:
1. Stand up hosted `dc-cite-ci` GitHub App: validates every PR touching a
   contract file, comments the regulatory-citation diff, blocks merge on
   uncited PII fields. €19/mo per repo, €49/mo for organisations.
2. Add CCPA, UK GDPR, LGPD coverage to the bundled citation map.
3. Offer consulting engagement (€60-80/h) to teams needing custom
   jurisdiction coverage or integration help.

---

## Assumptions and risks

- ODCS v3.x adoption continues. If ODCS forks or dies, the wedge evaporates.
- Regulatory text in the bundled map is verbatim from public EU OJ / US CFR.
  Any OJ URL change requires a rules-update release, but no legal risk.
- No GDPR/HIPAA legal advice is provided or implied; tool is for engineering
  traceability only. SECURITY.md states this explicitly.
