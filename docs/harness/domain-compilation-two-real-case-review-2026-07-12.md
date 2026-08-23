# Domain Compilation Contract — Two Real-Case Review (2026-07-12)

## Cases executed

| Case | Target / platform distinction | Verdict | Why conditional |
|---|---|---|---|
| X / AYi China AI power-chain seed | Public X metadata, partial article preview, Bloomberg video, attributable secondary report; logged-out public-web recovery only | `conditionally_feasible` | Original Goldman report unavailable; power-first ranking not corroborated by secondary report. |
| China AI thermal commercial-proof pass | CNINFO statutory 2025 report PDFs, page-level local extraction; public-PDF + local extraction platform | `conditionally_feasible` | Data-center/compute-adjacent segment proof exists, but AI-only and liquid-cooling-only economics remain unseparated. |

Machine artifacts:

- `trading-agent/data/users/feige/research/contract_bundles/2026-07-12/x-ayi-china-ai-power-chain-*.json`
- `trading-agent/data/users/feige/research/contract_bundles/2026-07-12/china-ai-thermal-commercial-proof-*.json`
- shared config: `.../public-source-plus-local-pdf-platform-config-v0.json`

Both passed `nous-os validate contracts` against `research-source-intake-spec-v0.json` with `verdict=conditionally_feasible` and zero structural issues.

## What repeated across real cases

1. **Scope is the central missing field.** The relevant distinction is not merely primary vs secondary. It is `what exactly does this evidence establish?` versus `what it explicitly cannot establish?`
   - Media summary can corroborate basket coverage but not original report wording/ranking.
   - Data-service segment proves data-center commercial exposure but not AI-only revenue.

2. **Provenance needs granularity.** `provenance` must include not just a URL but retrieval method, document/page location where relevant, observed time, and whether a statement is issuer disclosure, media attribution, or model inference.

3. **Counterexamples are practical.** In both cases a single counterexample prevents the common overclaim:
   - coverage list != power-first ranking;
   - data-center segment != AI-only revenue.

4. **Target and platform remain distinct in practice.** The target was evidence/content state; the platform was the access/processing capability. The same target could produce a different verdict under an authenticated research platform or a fuller issuer disclosure.

5. **`conditionally_feasible` is not a weak result.** It is the correct outcome when a workflow can produce a bounded, useful conclusion but cannot support the stronger claim people may want to make.

## Field candidates — do not standardize yet

After only two real cases, retain `SpecIR v0` / `TargetDescription v0` / `PlatformConfig v0` / `VerificationReport v0` unchanged. Collect one more case before changing the contract.

Candidates to test in the third case:

```yaml
claim_scope:
  establishes: [bounded claim]
  does_not_establish: [prohibited inference]
evidence_refs:
  - source: url_or_artifact
    locator: page|paragraph|frame|field
    retrieval_method: public_html|pdf_text|syndication|manual
    evidence_tier: issuer|primary|attributable_secondary|preview|inference
```

Promotion condition: add these fields to a deterministic schema only if the third case also needs them to prevent a material false upgrade.

## Human boundary

The validator checks structure and qualified verdict logic. It does not determine truth, business value, or acceptable residual risk. A named human remains responsible for whether a conditional evidence package is sufficient for publication, investment research, or high-consequence use.
