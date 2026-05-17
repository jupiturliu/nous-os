# NOUS OS Research Line — Anchor Atlas

The curated map of external work that surrounds the NOUS OS research line on human-AI co-evolution. This atlas is a **living document**. Entries are added as we read them. The public mirror is `nousos.ai/research-line-atlas.html`.

## How to read this atlas

Every entry has the same four lines:

- **What it is** — name, year, kind (paper / book / product / podcast / essay).
- **Claim** — the core argument or function in ≤ 1 sentence.
- **Where we share** — what part of NOUS OS theory or method it reinforces.
- **Where we differ / what we add** — the specific position NOUS OS holds vs this anchor.

Plus a **status** flag:

- `note-written` — full 1-page inbound note exists in `docs/research-line/inbound/`.
- `scanned` — read briefly, positioning recorded here, no full note yet.
- `queued` — known to exist, queued for the next reading cycle.

When an external anchor moves from `queued` → `scanned` → `note-written` it is *not* an upgrade in importance; it is an upgrade in our **depth of engagement** with that work.

---

## 1 · Foundational thought (the lineage)

### Vannevar Bush · "As We May Think" (1945, *The Atlantic*)
- **What it is:** essay introducing the Memex.
- **Claim:** human knowledge work is bottlenecked by retrieval, not generation; the right tool extends memory without replacing thinking.
- **Where we share:** the augmentation framing — tools extend, do not replace.
- **Where we differ / what we add:** Bush imagined hardware; we instrument the *loop* between human and AI as the measurable unit.
- **Status:** `scanned`

### Doug Engelbart · "Augmenting Human Intellect: A Conceptual Framework" (1962, SRI report)
- **What it is:** the foundational augmentation manifesto + later NLS demo.
- **Claim:** capability is a coupling of human, language, tool, training; the right design loop raises civilization's "H-LAM/T" capability.
- **Where we share:** explicit "human at the center" language, system-level thinking.
- **Where we differ / what we add:** Engelbart did not live to confront LLM-era misalignment risk; the NOUS OS boundary taxonomy and capability-without-AI delta are LLM-era additions to his frame.
- **Status:** `scanned`

### Seymour Papert · *Mindstorms: Children, Computers, and Powerful Ideas* (1980)
- **What it is:** the constructionism manifesto.
- **Claim:** children learn most when they build; the role of computers in learning is to enable construction, not to deliver answers.
- **Where we share:** student-as-builder framing; the Sandbox is constructionism re-instantiated with AI.
- **Where we differ / what we add:** Papert used LOGO + minimal scaffolding; we add explicit *boundary* phases and source-check phases because LLM output looks confident in ways LOGO never did.
- **Status:** `scanned`

### Lev Vygotsky · Zone of Proximal Development (1934 / 1978 English trans.)
- **What it is:** developmental psychology framework, now foundational for scaffolding theory.
- **Claim:** learning happens in the zone between what a learner can do alone and what they can do with help; scaffolding withdraws as competence grows.
- **Where we share:** the entire Sandbox loop is dynamic AI-as-scaffold in the ZPD.
- **Where we differ / what we add:** we make the *withdrawal* of scaffolding measurable via the capability-without-AI delta instrument.
- **Status:** `scanned`

### J.C.R. Licklider · "Man-Computer Symbiosis" (1960)
- **What it is:** essay anticipating computers as cognitive partners.
- **Claim:** the most productive computing era will be a symbiosis between human and machine, not full automation.
- **Where we share:** the literal word *symbiosis* — same lineage.
- **Where we differ / what we add:** Licklider's "symbiosis" was speculative; ours is operational with measurable boundary integrity.
- **Status:** `queued`

---

## 2 · Academic — Cognitive science (the reverse front)

### Risko & Gilbert · "Cognitive Offloading" (2016, *Trends in Cognitive Sciences*)
- **What it is:** integrative review of cognitive offloading.
- **Claim:** humans systematically offload memory, calculation, and decision-making onto tools; this changes internal cognition, often costing native capability.
- **Where we share:** the descriptive framing — offloading does happen, does cost.
- **Where we differ / what we add:** the central NOUS OS question is the **reverse**: under what *conditions* does offloading make humans **stronger** rather than weaker? This is the literature gap we sit in.
- **Status:** `queued`

### Sparrow, Liu & Wegner · "Google Effects on Memory" (2011, *Science*)
- **What it is:** empirical study showing people remember less when they know they can re-look-up.
- **Claim:** access to external information changes what we encode internally.
- **Where we share:** validates that the offloading concern is empirically real.
- **Where we differ / what we add:** they did not test interventions that flip the effect. We do.
- **Status:** `queued`

### Benjamin Storm & colleagues · "Saving" effect on memory (various, 2014+)
- **What it is:** experiments on how saving a file changes memory for prior material.
- **Claim:** the act of externalizing memory can either free or impoverish the internal trace, depending on conditions.
- **Where we share:** *depending on conditions* — exactly the conditional we want to characterize.
- **Where we differ / what we add:** we move from file-saving to AI-mediated learning; the "conditions" become design parameters of a scaffold.
- **Status:** `queued`

### Barry Zimmerman · Self-Regulated Learning (SRL) (1989+, extensive corpus)
- **What it is:** dominant academic framework for student self-regulation.
- **Claim:** effective learners cycle forethought → performance → self-reflection; SRL is teachable.
- **Where we share:** the Sandbox 6-phase loop is an AI-native SRL instantiation. The reflection card directly maps to SRL's self-reflection phase.
- **Where we differ / what we add:** SRL is silent on what happens when a confident AI is in the middle. The boundary phases (3, 5) are an AI-era addition to SRL.
- **Status:** `queued`

### John Sweller · Cognitive Load Theory (1988+)
- **What it is:** instructional design framework grounded in working-memory constraints.
- **Claim:** intrinsic / extraneous / germane load determines what is learned; design that minimizes extraneous load while maximizing germane load wins.
- **Where we share:** our 20-minute, 6-phase, 3-4 minute-per-phase structure is implicitly CLT-respectful.
- **Where we differ / what we add:** we should explicitly cite CLT going forward; the current Sandbox documentation does not.
- **Status:** `queued`

---

## 3 · Academic — AI Literacy / HCI (the contemporary peers)

### Duri Long & Brian Magerko · "What is AI Literacy? Competencies and Design Considerations" (2020, CHI)
- **What it is:** widely-cited conceptual paper proposing a 16-competency framework for AI literacy.
- **Claim:** AI literacy is multi-dimensional and includes critical evaluation, ethics, programmability awareness, etc.
- **Where we share:** essentially the same target audience (general public, K-12 ramp).
- **Where we differ / what we add:** they offer a **descriptive taxonomy**; we offer an **instrumented loop with measurable outcomes**. Their 16 competencies are largely cognitive checklists; ours is a 20-minute behavioral protocol with capability-delta measurement. We sit downstream as a way to operationalize their framework.
- **Status:** `note-written` → `inbound/2026-05-17-long-magerko-2020.md`

### UNESCO · *AI Competency Framework for Students* (2024)
- **What it is:** international policy framework.
- **Claim:** four core dimensions × twelve competencies students should develop around AI.
- **Where we share:** student-facing focus, public-interest framing.
- **Where we differ / what we add:** UNESCO writes standards; we run experiments. The framework is consumer of evidence; we are a producer of (small-N) evidence.
- **Status:** `queued`

### Stanford HAI (Human-Centered AI Institute) · ongoing publications
- **What it is:** Stanford's institutional umbrella for human-centered AI work.
- **Claim:** AI should be developed alongside humans, not at them; the institute publishes white papers, policy briefs, and CRAFT (centering responsible AI in classroom teaching) materials.
- **Where we share:** the "human-centered" framing.
- **Where we differ / what we add:** Stanford HAI is a publishing institution; we are an instrumented practice. We can read their CRAFT materials and import lessons.
- **Status:** `queued`

### MIT Media Lab · Lifelong Kindergarten (Mitchel Resnick), Personal Robots (Cynthia Breazeal)
- **What it is:** two adjacent groups producing work on creative learning + social-robot co-learning.
- **Claim:** learning compounds best when projects, peers, passion, and play are present; AI partners can support these as long as they preserve the learner's authorship.
- **Where we share:** the "preserve authorship" line is identical to ours.
- **Where we differ / what we add:** they focus on creative-project authorship; we focus on research-loop authorship.
- **Status:** `queued`

### CHI / CSCW / Learning Sciences recent papers on prompt scaffolding (2024-2026)
- **What it is:** an emerging body of empirical work on AI scaffolding patterns in education.
- **Claim:** specific prompt designs (e.g., "ask the AI to ask you questions first") improve learning outcomes.
- **Where we share:** we are downstream practitioners of these patterns.
- **Where we differ / what we add:** most of these papers measure satisfaction or correctness; we measure capability without AI, which is rare. We should systematically scan recent CHI proceedings.
- **Status:** `queued`

---

## 4 · Industry — research & alignment voices

### Anthropic · Constitutional AI + research on tool use, alignment, interpretability
- **What it is:** a body of published work on making AI systems behave within explicit value boundaries.
- **Claim:** structured human feedback + explicit constitutional rules produce better-aligned model behavior than pure RLHF.
- **Where we share:** the *explicit-boundary* design philosophy.
- **Where we differ / what we add:** Anthropic's boundaries are model-side (what the AI is allowed to do); ours are *interaction-side* (what the human commits to retain). These are complementary halves of a symbiosis.
- **Status:** `queued`

### DeepMind · scalable oversight + scientific-discovery work
- **What it is:** technical alignment research + AlphaFold / AlphaProof / AlphaProteo lines.
- **Claim:** AI can augment scientific discovery; scalable oversight is solvable.
- **Where we share:** the augmentation thesis.
- **Where we differ / what we add:** DeepMind's evidence is on AI capability; ours is on human capability when AI is present.
- **Status:** `queued`

### OpenAI · "GPTs in the classroom" + educator partnership reports
- **What it is:** deployment-study work on AI in education contexts.
- **Claim:** GPTs as tutors, study helpers, etc.
- **Where we share:** the practical "AI in education" focus.
- **Where we differ / what we add:** OpenAI's measurement is usage + satisfaction; ours is human capability delta. We should track their public studies but treat them as product reports, not research.
- **Status:** `queued`

### Stuart Russell · *Human Compatible* (2019, Viking)
- **What it is:** book-length argument for redesigning AI around human preferences and uncertainty about objectives.
- **Claim:** AI safety requires AI systems that explicitly defer to humans and remain uncertain about goals.
- **Where we share:** the responsibility-stays-with-human stance.
- **Where we differ / what we add:** Russell is at the alignment-policy layer; we are at the daily-interaction-design layer. His policy frame implies our interaction design.
- **Status:** `queued`

### Dario Amodei · "Machines of Loving Grace" (2024, essay)
- **What it is:** Anthropic CEO's published essay on benevolent AI futures.
- **Claim:** if alignment is solved, the next decade could see profound human gains in health, science, education, freedom.
- **Where we share:** the optimistic-but-conditional vision.
- **Where we differ / what we add:** Amodei describes the destination; we propose the per-session protocol that makes any one human less likely to lose capability on the way there.
- **Status:** `queued`

---

## 5 · Top products (the same-shape attempts)

### Khan Academy · Khanmigo
- **What it is:** a Khan-Academy-integrated AI tutor built atop GPT-4.
- **Claim:** Socratic AI tutoring at scale, with safety rails for under-18 users.
- **Where we share:** the Socratic / hints-not-answers stance.
- **Where we differ / what we add:** Khanmigo *is* an AI; the NOUS OS Sandbox is a protocol that wraps **any** AI the student chooses to use. Khanmigo's design is the closest commercial cousin to NOUS OS philosophy and the most important benchmark to study.
- **Status:** `queued`

### Google · NotebookLM
- **What it is:** a notebook-style product that grounds AI responses in user-supplied sources, with novel "audio overview" feature.
- **Claim:** source-grounded AI is more trustworthy and more useful.
- **Where we share:** Sandbox phase 4 (source check) is directly aligned with NotebookLM's source-grounding ethos.
- **Where we differ / what we add:** NotebookLM optimizes one phase of the loop (source grounding); we structure the full 6-phase loop and explicitly include the human-boundary and reflection phases.
- **Status:** `note-written` → `inbound/2026-05-17-notebooklm-product-walk.md`

### Cursor · AI pair programmer
- **What it is:** AI-augmented code editor with explicit suggest-vs-apply boundaries.
- **Claim:** developer productivity rises when AI suggestions are explicitly accept-or-reject rather than silently applied.
- **Where we share:** the explicit *accept-or-reject* boundary, directly analogous to our boundary phase.
- **Where we differ / what we add:** Cursor proves the pattern in the code domain; we propose the same pattern for research/learning.
- **Status:** `queued`

### Anthropic · Claude Code (the product running this conversation)
- **What it is:** terminal-native agentic coding assistant.
- **Claim:** an agent can do real engineering work safely if boundaries (permissions, tool use, plan mode) are explicit.
- **Where we share:** every key design choice — explicit permissions, plan mode, transparent diffs.
- **Where we differ / what we add:** Claude Code is the *engineering* instantiation of NOUS OS principles; the Sandbox is the *learning* instantiation. They are sibling products of the same philosophy.
- **Status:** `scanned`

### Cognition · Devin / Replit Agent · Operator (OpenAI)
- **What it is:** more aggressive autonomous-agent products.
- **Claim:** agents can do longer-horizon tasks unattended.
- **Where we share:** they share the agentic substrate.
- **Where we differ / what we add:** these are *autonomy-maximizing* designs; NOUS OS is explicitly *symbiosis-maximizing*. Useful contrast points.
- **Status:** `queued`

### Granola / Mem / similar "AI + your notes" products
- **What it is:** meeting-notes products that draft from transcript, human edits before save.
- **Claim:** drafting is cheap; human curation is the value-add.
- **Where we share:** the human-curates-before-commits pattern.
- **Where we differ / what we add:** Granola optimizes a workflow product; we extract the pattern and codify it as a loop principle.
- **Status:** `queued`

### Perplexity / Phind · cited-search AI
- **What it is:** search products that produce answers grounded in cited sources.
- **Claim:** AI search is better than non-cited AI chat.
- **Where we share:** source primacy.
- **Where we differ / what we add:** they optimize answer-with-citations; we incorporate source-check as one explicitly-bounded phase, not the whole interaction.
- **Status:** `queued`

---

## 6 · Individual essays & podcasts (the living thinkers)

### Andy Matuschak (independent researcher) · writing + appearances
- **What it is:** ongoing essays on tools for thought, spaced repetition, learning environments. Mostly at andymatuschak.org and Patreon updates.
- **Claim:** most "tools for thought" are not transformative; transformative ones change the medium of thought itself.
- **Where we share:** the medium-changes-thought framing.
- **Where we differ / what we add:** Matuschak focuses on individual cognition; we focus on the human-AI **pair**. His vocabulary will be useful for L3 (knowledge loop).
- **Status:** `note-written` → `inbound/2026-05-17-matuschak-nielsen-2019.md`

### Michael Nielsen · *Reinventing Discovery* + Matuschak collab essays
- **What it is:** physicist + writer on open science, tools for thought.
- **Claim:** new mediums of representation enable new kinds of thought.
- **Where we share:** representation-as-cognitive-substrate stance.
- **Where we differ / what we add:** Nielsen's essays are inspirational and ungrounded in trials; we run trials.
- **Status:** `scanned` (jointly with Matuschak 2019 essay)

### Bret Victor · "Inventing on Principle", "Magic Ink", *Dynamicland*
- **What it is:** designer/researcher producing influential demos of dynamic representation.
- **Claim:** thought is constrained by representation; better representation enables better thought.
- **Where we share:** the deeply held belief in representation-as-cognition.
- **Where we differ / what we add:** Victor's work is largely demonstrative; we add empirical loops.
- **Status:** `queued`

### Ethan Mollick · *Co-Intelligence* (2024) + *One Useful Thing* Substack
- **What it is:** Wharton professor's book + weekly newsletter on practical AI use.
- **Claim:** treat AI as a co-worker; experiment widely; expect rapid capability shifts.
- **Where we share:** the practical-empirical attitude.
- **Where we differ / what we add:** Mollick is **descriptive and adult-facing**; NOUS OS is **prescriptive, instrumented, and student-facing** in L1. Both can exist.
- **Status:** `queued` (priority for next inbound)

### Cal Newport · *Deep Work*, *Slow Productivity*, podcast
- **What it is:** computer scientist + author warning about attention-shredding tech.
- **Claim:** deep cognitive work requires uninterrupted attention; modern tools fight against this.
- **Where we share:** the concern that AI use without design can shred attention.
- **Where we differ / what we add:** Newport's stance leans toward minimalism / avoidance; we propose that *scaffolded* AI use can produce deep work, not destroy it. We are the conditional "with the right design" case.
- **Status:** `queued`

### Dwarkesh Patel · *Dwarkesh Podcast* (formerly *Lunar Society*)
- **What it is:** long-form interviews with top AI researchers and thinkers.
- **Claim:** N/A — interview format.
- **Where we share:** access to current AI-research thinking before it surfaces in papers.
- **Where we differ / what we add:** consumer relationship — we should pick 1-2 episodes per quarter for inbound notes.
- **Status:** `queued`

### Ezra Klein Show (NYT podcast) · AI/society episodes
- **What it is:** mainstream public-interest podcast with frequent AI episodes (e.g., conversations with Karen Hao, Dario Amodei, Demis Hassabis).
- **Claim:** N/A — interview format.
- **Where we share:** connection to broader societal AI discourse.
- **Where we differ / what we add:** Ezra Klein is mainstream-discourse-shaping; we feed our research-line writing back into that discourse over time.
- **Status:** `queued`

### Tyler Cowen · *Marginal Revolution* + *Conversations with Tyler*
- **What it is:** economist's blog + interview podcast.
- **Claim:** economists' takes on AI's distributional + cognitive impact, often contrarian and useful.
- **Where we share:** willingness to ask "what does this do to people" rather than "what can it do."
- **Where we differ / what we add:** Cowen is macro-economic; we are individual-cognitive. Cross-pollination via posts.
- **Status:** `queued`

### Ben Thompson · *Stratechery* (paid newsletter)
- **What it is:** strategic analysis of tech industry, weekly + Daily Updates.
- **Claim:** AI is a platform shift; strategy logic from prior platform shifts applies.
- **Where we share:** product-strategy literacy informs our "what is happening in product land" tracking.
- **Where we differ / what we add:** Thompson is product-strategy-focused; we are research-method-focused. Different lens, complementary.
- **Status:** `queued`

### Latent Space podcast (Swyx + others)
- **What it is:** AI engineering practitioners' podcast.
- **Claim:** N/A — practitioner format.
- **Where we share:** stays current on what's deployable.
- **Where we differ / what we add:** we are the principles-and-evidence layer; Latent Space is the deployable-engineering layer.
- **Status:** `queued`

### Lex Fridman Podcast · AI conversations
- **What it is:** long-form interviews including many AI researchers.
- **Claim:** N/A — interview format.
- **Where we share:** broad-public AI discourse.
- **Where we differ / what we add:** signal-to-noise variable; pick selectively.
- **Status:** `queued`

### 晚点 LatePost (Chinese) + 张小珺 商业访谈
- **What it is:** Chinese-language tech publication + creator-focused podcast.
- **Claim:** N/A — interview / journalism format.
- **Where we share:** access to Chinese AI ecosystem thinking, often missing from Western feeds.
- **Where we differ / what we add:** an L1-capture lane the cron will not easily reach (no clean RSS); we will manually feed Chinese-source inbound notes when something surfaces.
- **Status:** `queued`

---

## 7 · The empty position (where we stand)

After mapping all of the above, the position that remains conspicuously empty is:

> **Empirical, instrumented, public protocols that measure whether a *human* becomes more capable in AI's absence after AI-assisted work.**

Most cognitive-offloading work measures the negative case. Most AI-literacy work writes taxonomies. Most product studies measure usage and satisfaction. Most industry research measures the AI. Most individual essays speculate. The protocol-with-measured-capability-delta position is largely empty.

That is where this research line lives.

---

## 8 · Reading discipline

How this atlas stays alive:

- Inbound capture (L1 cron, eventually) produces a daily raw inbox.
- Weekly triage (L2) promotes 1-3 candidates per week to inbound notes here.
- New inbound notes are appended to the appropriate bucket above with status flipped to `note-written` and a link to `inbound/YYYY-MM-DD-<slug>.md`.
- Every quarterly synthesis writes up what new entries arrived and what they changed about our internal thinking.

The atlas is not a reading list. It is the cumulative record of what we have engaged with, how engaged we are, and where we differ. When you cannot answer "where do we differ?" for an entry, the entry has not really been read.
