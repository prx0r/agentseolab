# HACKATHON NORTH STAR — DevNetwork [API + Cloud + AI] Hackathon 2026

Source: https://api-cloud-ai-hackathon-2026.devpost.com/ (fetched 2026-08-24)
This file is the authoritative external target. `northstar.md` (product thesis) +
this file (competition constraints) together govern all build decisions.

---

## Key facts

| Item | Value |
| --- | --- |
| Deadline | **Sep 3, 2026 @ 10:00am PDT** (~10 days out) |
| Online period | Aug 17 – Sep 3, 2026 |
| In person + awards | Santa Clara Convention Center, Sep 2–3, 2026 |
| Participants | 975 |
| Total prizes | $39,500 |
| Our challenge | **name.com — Domain API Challenge** |

## name.com — Domain API Challenge

**Prize:** $2,000 — 1st: $1500 Amazon gift card · 2nd: $500
Contact: daisy.edwards@identity.digital

> Build a product powered by the name.com API. Integrate it into a working
> product using domain search, availability checks, registration, or DNS
> management as a core part of the build. Format is open. Build something new
> or extend an existing project, as long as the name.com API is functionally
> central to what you ship. Judges want to see the API doing something the
> product actually depends on.

### Judging criteria (verbatim)

1. **API integration depth**: How central is the name.com API to the product.
   Judges favor integrations that combine multiple endpoints (search plus
   registration plus DNS, for example) over a single surface-level call.
2. **Creativity and originality**: Is the use case distinct. Judges favor
   unexpected applications over incremental tweaks on existing domain search tools.
3. **Technical execution**: Code quality, architecture decisions, and how well
   the team handled edge cases.
4. **Real-world viability**: Could this plausibly become a product or feature
   people would use. Market relevance and clarity of the value proposition.
5. **Presentation and demo**: Clarity of the final walkthrough. Judges want to
   see the integration in action, not just slides.

### General hackathon judging criteria
- Progress — how much progress did you make?
- Concept — does it solve a real problem?
- Feasibility — could this become a startup or company?

## What this means for DomainArena (mapping)

| Criterion | DomainArena answer | Status |
| --- | --- | --- |
| Integration depth | Search → CheckAvailability → GetPricing → CreateDomain → DNS records → read-back receipt | client built; live search verified; registration blocked on sandbox creds |
| Creativity/originality | NOT another generator: an empirical decision engine (`recommend_domain`) measuring whether a domain causes correct agent selection + verified task success | core implemented |
| Technical execution | Controlled experiments, AB/BA, position-stratified estimands, hidden verifiers, evidence receipts, edge-case contract tests (401/429/5xx/premium/stale availability) | 37 tests green |
| Viability | Recommendation intelligence layer for name.com / Lovable / Railway-style builders; every recommendation converts into a registration | pitch ready |
| Presentation/demo | 3 deterministic fixtures, <4 min walkthrough, approval-gated registration on screen | fixtures hardcoded |

## Submission requirements checklist

- [ ] Devpost project page: name, pitch, screenshots, write-up
- [ ] Public repo (prx0r/agentseolab) with setup instructions
- [ ] Demo video 2–4 min showing integration end-to-end
- [ ] name.com API visibly doing real work (live search at minimum)
- [ ] Multiple endpoints demonstrated (search + checkAvailability + pricing + register + DNS)
- [ ] Edge cases handled visibly (premium filtering, budget elimination, recheck-before-buy)
- [ ] Register before deadline; monitor Updates page for rule changes

## Deadlines & risks

- Sandbox credentials currently 403 — if unfixable, demo registration via
  production account with explicit user approval on screen, or request sandbox
  access from daisy.edwards@identity.digital.
- Project gallery was not yet published at fetch time; re-check for competing
  name.com entries periodically.

## Other sponsor challenges (context only — we are entering name.com's)

Perfect ($2.5k), Foxit ($1k), Doctavian ($1k), Nutrient ($1.5k), SerpApi ($3k),
Xano ($2.5k). Overall winner: $12,500. A name.com entry can also compete for
the overall prize.
