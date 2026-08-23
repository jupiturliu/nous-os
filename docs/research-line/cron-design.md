# NOUS OS Research Line — Cron Design

This document specifies the L1 capture cron that feeds external thinking into the NOUS OS Research Line every day. It is the concrete implementation of the three-tier external-input loop defined in `research-line.md` § 6.

## Why

The north star — *compounding wisdom in human-AI pairs* — cannot be served by internal work alone. NOUS OS must continuously absorb external thinking (academic preprints, industry research, top products, individual essays / podcasts) without drowning in firehose noise. Daily-fresh input is the operating mechanism that turns the north star from a philosophical claim into a discipline.

## Architecture: 3 tiers

```text
L1 · Capture     daily       nous_os.workflows.research_line
                              → docs/research-line/inbound/_inbox/YYYY-MM-DD.md
                              → opened as a PR by .github/workflows/research-line-capture.yml

L2 · Triage      weekly      human operator reviews open inbox PRs.
                              Merge / close / transform options on each PR.

L3 · Synthesis   quarterly   docs/research-line/synthesis/YYYY-QN.md
                              "What we read, what we changed because of it."
```

## L1 capture — what the cron actually does

### Schedule

Daily at **07:15 UTC** (one window per day, via `.github/workflows/research-line-capture.yml`). Also available as a `workflow_dispatch` trigger for ad-hoc captures with optional `max_age_days` override.

### Sources (current set — keep small)

The configured source list lives in `nous_os.workflows.research_line::SOURCES`. The design point is **≤ 8 sources** to keep noise low. Initial set:

| ID | Title | Feed | Anchor bucket |
|---|---|---|---|
| `arxiv-cs-hc` | arXiv cs.HC | http://export.arxiv.org/rss/cs.HC | 3 · AI literacy / HCI |
| `arxiv-cs-cy` | arXiv cs.CY | http://export.arxiv.org/rss/cs.CY | 3 · AI literacy / HCI |
| `mollick-one-useful-thing` | Mollick · One Useful Thing | https://www.oneusefulthing.org/feed | 6 · Individual essays |
| `matuschak-blog` | Andy Matuschak | https://andymatuschak.org/feed.xml | 6 · Individual essays |
| `openai-news` | OpenAI · News | https://openai.com/news/rss.xml | 4 · Industry research |

When a feed URL changes or goes dead, update the `SOURCES` list in the script and **add the change to the next quarterly synthesis** so we know what coverage shifted.

### Keyword filter

The filter is a flat list of anchor keywords (`nous_os.workflows.research_line::KEYWORDS`). An entry is kept if its title or summary contains any keyword (case-insensitive substring). Order does not matter. Initial keywords are deliberately specific:

- *AI literacy*, *AI tutor*, *AI scaffolding*, *AI in education*, *AI in the classroom*
- *cognitive offloading*, *tools for thought*, *self-regulated learning*, *metacognition*
- *human-AI*, *co-evolution*, *human agency*, *boundary*, *ZPD*, *scaffolding*
- *capability delta*, *calibrated trust*, *transformative tool*
- *constitutional AI*, *alignment*, *interpretability*

**Anti-pattern:** Do not add broad words like *AI* or *learning* on their own — they produce firehose noise. Any new keyword candidate should have anchor-level specificity.

### Recency window

`--max-age-days` (default 2) drops entries older than the window. Two days is intentionally short: we want yesterday's surprises, not a backlog. The default matches a one-source-per-day cadence; if cron misses one day the next run still catches recent items.

### Output shape

Daily markdown file: `docs/research-line/inbound/_inbox/YYYY-MM-DD.md`

- YAML front-matter: `layer: L1`, `status: raw`, `captured: YYYY-MM-DD`
- Per-source section: source title, URL, kept-count, error if fetch failed
- Per-entry block: title, link, published date, matched keywords, truncated summary

The file is plain markdown so it can be diff-reviewed in a PR. The capture script never writes anywhere else and never deploys to the site.

### Deploy stance

`apps/web/site-manifest.yaml` does **not** ship `_inbox/` contents. Only L2-promoted notes (the top-level `docs/research-line/inbound/*.md`) reach `nousos.ai`. Raw L1 is repo-internal until triage.

## L2 triage — what the operator does

Daily review of open `L1 capture · YYYY-MM-DD` PRs (one per day). Each PR has three options:

1. **Merge** — the day's inbox file lands in `master`. Visible in the repo, not on the site. Useful for archival / forensics.
2. **Close** — discard the day entirely. No record kept. Use when nothing landed worth even archiving.
3. **Transform first** — promote 1–3 entries to full 1-page inbound notes at `docs/research-line/inbound/*.md` using the `_template.md`. Update `docs/research-line/anchor-atlas.md` and `research-line-atlas.html` to flip the corresponding anchor from `queued`/`scanned` to `note-written`. *Then* merge the PR.

Recommended cadence: ~5 minutes daily, ~15 minutes weekly for any transforms. Total ~50 minutes / week, durable because it produces public-corpus material.

## L3 synthesis — quarterly

Once per quarter, write `docs/research-line/synthesis/YYYY-QN.md`:

- N of L1 days captured / N of L2 transforms produced
- The 3-5 most influential inbound notes of the quarter
- What changed in our internal practice as a result (specific docs, tests, sub-line decisions)
- What we noticed about coverage gaps (new sources to add? old sources to remove?)
- One paragraph: did this quarter move (a)/(b)/(c) of the research line in any measurable way?

## What this design intentionally is NOT

- **Not an LLM-judged feed.** L1 is pure pattern matching. Adding LLM scoring at L1 introduces opaque selection and breaks reproducibility.
- **Not auto-merging.** Every entry that lands in the corpus passes a human gate.
- **Not deployed to the site.** Raw L1 is operator-internal; only L2-promoted notes are public.
- **Not aspirational.** If a source's feed is dead for two weeks, remove it from `SOURCES` and write down why in the next quarterly synthesis. Coverage decisions are explicit, not implicit.
- **Not multi-actor.** One operator does L2 triage. Multi-rater inter-reliability work belongs to per-session reviews, not to the inbound pipe.

## Failure modes and how we notice

- **Cron stops firing.** Visible as missing dated files in `_inbox/`. The next quarterly synthesis must call out gaps in the YYYY-MM-DD sequence.
- **All sources error.** The PR for that day still opens with `0/N sources fetched OK`, surfacing the failure in the PR title's diff (an empty file is a signal).
- **Operator falls behind on triage.** Open inbox PRs accumulate. The discipline is: do not let more than 7 open PRs queue. Past 7, do a quick `close-without-merge` bulk pass on the oldest ones.
- **Source goes high-volume / low-signal.** Watch for an L2 promotion rate that drops near zero for a source over a quarter. Remove the source.

## Verification

- `nous-os run research-line --profile research --dry-run` — confirms feed parsing, keyword matching, and markdown rendering end-to-end without writing anything.
- `python3 -m unittest tests.test_research_line_capture -v` — unit tests against fixture RSS / Atom data. No network.
- Workflow integration is verified end-to-end the first time the cron fires (or by `gh workflow run "Research Line · L1 daily capture"`).

## Status

- Implementation: complete — script, workflow, and tests live as of 2026-05-17.
- First scheduled run: next 07:15 UTC after the workflow is merged to master.
- First L2 triage cycle: starts when the first PR opens.
