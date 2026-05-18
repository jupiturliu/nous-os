# NOUS OS Research Line: Human-AI Co-Evolution Studies (HAICES)

This document is the canonical internal specification for the NOUS OS research line. The public-facing mirror lives at `research-line.html` and ships to `nousos.ai/research-line.html`.

The research line is **internal** in the sense that we do not currently target a peer-reviewed venue. It is **disciplined** in the sense that it follows the same evidence rules we would use if we did.

---

## 1 · North Star

> **Under what conditions does a human-AI pair accumulate compounding wisdom — not merely accelerated output, not merely personalized convenience — over months and years?**

This is the framing the research line is ultimately answerable to. It is intentionally long-horizon and not measurable in a single session. The two near-term instruments below exist to feed it.

## 2 · Near-term instruments

The north star is not directly testable. These two questions are.

| Instrument | Question | Test surface | Time horizon |
|---|---|---|---|
| **(a) Capability-without-AI delta** | After a scaffolded AI-assisted loop, does the human perform measurably better on a similar task **when AI is absent**? | Student Sandbox v1 trials with before/after task | per-session, weeks |
| **(b) Calibrated trust + responsibility retention** | Over repeated cycles, does the human delegate the right parts and retain the right parts; does trust track evidence quality rather than fluency? | trading-agent reviewed outcomes; longitudinal Sandbox cohort | per-cycle, months |

If (a) and (b) trend up over many cycles across many people, that is **evidence** for the north star. If they do not, the north star is wishful.

## 3 · Three sub-lines

Each sub-line has a clear study unit, a baseline condition, and a primary boundary it tests.

### L1 · Learning loop (Student Sandbox)

- **Question:** Does a 20-minute scaffolded human-AI loop produce a measurable Capability-without-AI delta (instrument a) vs both (i) no-AI baseline and (ii) cold-chat AI baseline?
- **Study unit:** one 20-minute Student Sandbox session + a delayed transfer task without AI access
- **Baselines:**
  - (i) student attempts same domain task with no AI
  - (ii) student attempts same domain task with a generic chat interface, no scaffold
- **Primary boundaries tested:** learning, fact, privacy, taste
- **Status:** N = 0 real trials at 2026-05-17. Scaffold + dry-run audit complete.

### L2 · Decision loop (trading-agent)

- **Question:** Does AI-augmented decision-making with explicit boundaries produce decisions humans can defend better, calibrate trust better, and learn from outcomes better over time (instrument b)?
- **Study unit:** one promoted candidate + post-outcome review packet
- **Baseline:** absent in the original trading-agent design; we can retrospectively bin reviews where boundary discipline was strong vs weak.
- **Primary boundaries tested:** decision, responsibility, value
- **Status:** ongoing. ~hundreds of candidates reviewed. No one has run the data through (b) yet — that is a meaningful gap in current NOUS OS practice.

### L3 · Knowledge loop (personal knowledge / Obsidian)

- **Question:** Does long-horizon human-AI memory interaction (Obsidian + TrustMem) produce compounding reflection capacity, or does it produce stale personalization and dependence?
- **Study unit:** an Obsidian section with 90 days of entries + a 90-day-later retrospective task
- **Baseline:** same person's pre-NOUS journaling segment, if available.
- **Primary boundaries tested:** identity, taste, responsibility
- **Status:** earliest. Methodology not yet pinned.

## 4 · Method commitments

These are the rules that turn a theory document into a research line.

1. **Pre-register predictions** before each session. Five-minute single-page document committing to what we expect to see. Stored at `docs/research-line/preregistration/`.
2. **Two raters when feasible.** Observer + a second reviewer (could be Claude / Codex) independently score the session using `self-evolution-metrics-v0.md`. Track inter-rater agreement even at N=1.
3. **De-identified review packets are the data.** Every session produces one review packet. Public publication is required (de-identified). They are the corpus, not folder-dust.
4. **Negative results are first-class.** If a session fails the prediction, write it up. Failure-to-publish-negatives is the single most common research-line corruption.
5. **Be explicit about N.** N=1 case studies are legitimate but must be labeled as such. Never write "students tend to…" at N≤5.
6. **No instrument inflation.** Resist adding metrics ad-hoc. New metrics require a quarterly synthesis to justify.

## 5 · Position in the literature

The full anchor atlas lives at `docs/research-line/anchor-atlas.md` (and its public mirror at `research-line.html#atlas`). Summary positioning:

| Tradition | Closest anchor | Where NOUS OS adds |
|---|---|---|
| Augmentation | Engelbart 1962, Bush 1945 | LLM-era boundary taxonomy + capability-delta instrument |
| Cognitive offloading | Risko & Gilbert 2016, Storm & Stone | Reverse question: when does offloading make people **stronger**? |
| Self-regulated learning | Zimmerman | AI-native instantiation of forethought → performance → reflection |
| AI literacy | Long & Magerko 2020, UNESCO 2024 | From descriptive taxonomy to instrumented loop |
| Tools for thought | Matuschak & Nielsen 2019 | From individual tools to explicit symbiosis |
| Practical AI advice | Mollick *Co-Intelligence* 2024 | From descriptive heuristics for adults to prescriptive 20-min protocol with measured outcomes |

The position the literature is most empty at: **measuring whether a person is more capable when AI is absent.** That is where this line is most concentrated.

## 6 · External-input loop (the daily-fresh-thinking machine)

The north star (c) cannot be served by internal work alone. NOUS OS must continuously absorb external thinking. Three-tier discipline:

| Tier | Cadence | Who | Output | Public? |
|---|---|---|---|---|
| L1 · Capture | daily | scheduled remote agent | `docs/research-line/inbound/_inbox/YYYY-MM-DD.md` — 5-10 raw candidates from RSS | partial (raw is noisy) |
| L2 · Triage | weekly | scheduled agent + human approval | promotes 1-3 candidates per week to full inbound notes at `docs/research-line/inbound/*.md` and a mirror HTML page | yes |
| L3 · Synthesis | quarterly | in-session Claude + human | `docs/research-line/synthesis/YYYY-QN.md` + mirror HTML — *"what we read, what we changed because of it"* | yes |

The cron implementation lives at `docs/research-line/cron-design.md` (to be written in the wave that actually sets up the routine). Until cron is live, the L2 inbound notes can be written manually whenever something worth keeping comes in.

## 7 · Cadence and outputs

| Frequency | Output | Public? |
|---|---|---|
| per session | review packet (Student Sandbox) or outcome review (trading-agent) | yes, de-identified |
| per session | `docs/research-line/session-review-index.md` row update | yes, de-identified |
| per inbound | 1-page note in `docs/research-line/inbound/*.md` + HTML mirror | yes |
| per week | L2 triage commit (1-3 new inbound notes) | yes |
| per quarter | synthesis writeup tying inbound + session data to "what we changed" | yes |
| per year | preprint / public artifact candidate (working paper, not peer-reviewed v0) | yes |

## 8 · What this line is **not**

- It is **not** a tutoring product.
- It is **not** a benchmark suite.
- It is **not** a substitute for peer review.
- It is **not** an excuse to write theory papers without running experiments.
- It is **not** infrastructure work disguised as research.

If we find ourselves making more boundary types or more metrics rather than more sessions, we have drifted.

## 9 · Current status (2026-05-17)

- Theory documents: complete (this doc + `human-ai-symbiosis-self-evolution.md` + `self-evolution-metrics-v0.md` + `human-ai-coevolution-model-v0.md` + `memory-philosophy-v0.md`)
- Anchor atlas: drafting (this wave)
- L1 sub-line: scaffold complete, **N=0 real trials**
- L2 sub-line: active in trading-agent, **no co-evolution lens applied to existing data yet**
- L3 sub-line: methodology not pinned
- L1 capture cron: not yet set up
- Pre-registration template: implemented
- Session review index: implemented, currently N=0 real sessions
- Research-to-product gate: implemented, first use expected after N=1
- Public research-line page: this wave

The single highest-leverage action remains: run one real Student Sandbox session and produce N=1.

## 10 · Related documents

- `docs/human-ai-symbiosis-self-evolution.md` — the theory anchor
- `docs/self-evolution-metrics-v0.md` — the measurement instrument
- `docs/human-ai-coevolution-model-v0.md` — the model
- `docs/memory-philosophy-v0.md` — memory governance
- `docs/research-line/anchor-atlas.md` — external work positioning (next wave)
- `docs/research-line/cron-design.md` — daily-input automation (later wave)
- `docs/research-line/session-review-index.md` — de-identified session ledger
- `docs/research-line/research-to-product-gate.md` — evidence gate for product changes
- `docs/student-sandbox-v1-recruitment.md` — Phase B recruitment templates
