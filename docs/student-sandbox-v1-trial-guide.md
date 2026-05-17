# NOUS OS Student Sandbox v1 Trial Guide

This guide runs one privacy-first, 20-minute high-school research learning session.

The purpose is not to let AI write the assignment. The purpose is to help a student practice using AI for hints, not final answers, while preserving human agency, source verification, values, and responsibility.

## Before the session

Prepare:

- one student-chosen research topic;
- assignment rubric or teacher instruction, if available;
- allowed source types;
- blank notes page;
- optional parent/teacher observer.

Privacy rule:

Do not record the student's full name, school name, email, family details, account details, or raw private prompt. If a private detail appears, redact it before saving any artifact.

What the v1 scaffold enforces vs what humans must enforce:

- **Software-enforced:** if the input contains an email, phone number, or SSN-style pattern, the scaffold drops the entire `student_intent` field and writes `[redacted-by-policy]` instead. `privacy.private_detail_detected` records that the input tripped a detector.
- **Human-enforced:** full names, school names, family details, and account details are **not** pattern-matchable; the scaffold cannot catch them. Observer and student must avoid typing them in the first place. When in doubt, write the topic area ("CRISPR ethics for biology class") instead of identifying context ("Mrs. Smith's class at Lincoln HS").

## 20-minute loop

| Minute | Phase | Student does | AI may help with | Student keeps |
|---:|---|---|---|---|
| 0-3 | Intent | Write the research question in their own words | clarify subquestions | goal and curiosity |
| 3-7 | AI first pass | ask for a learning plan, not an answer | concepts, vocabulary, source types, traps | which path to explore |
| 7-10 | Human boundary | choose privacy / facts / learning / decision / values boundary | restate and adapt around boundary | values and constraints |
| 10-14 | Source check | inspect two sources | checklist and critique | verification decision |
| 14-17 | AI second pass | revise the plan using boundary + source notes | next steps and uncertainty notes | final claim judgment |
| 17-20 | Reflection | complete reflection card | compare first and second pass | responsibility and next move |

## Student prompt script

Use this script as-is for the first trial:

```text
I am a high-school student researching: <topic>.
Do not write my final answer.
Help me make a 20-minute learning plan.
Ask what I already know, what sources I can use, and what boundary I want to keep.
Give me hints, source-check questions, and reflection prompts.
```

## Source checklist

For each source, ask:

- Can I find the original source, not only a summary?
- Who is the author or institution?
- Is the date current enough for this topic?
- What evidence is provided?
- What is opinion or interpretation?
- What would change my mind?

## Reflection card

The student answers these before drafting final assignment text:

- What did AI help with?
- What did I verify?
- What boundary did I add?
- What remains my responsibility?
- What would I ask differently next time?

## Parent / teacher observation questions

Optional observer records process observations only:

- Was AI acting like a tutor instead of a ghostwriter?
- Could the student explain the research question without AI?
- Did the student identify at least one source-quality issue?
- Did the student preserve their own judgment before drafting?
- Which instruction or boundary confused the student?

## Research-study note format

Safe observation note:

```text
Session date:
Topic area, not exact private prompt:
Boundary chosen:
Source check attempted: yes/no
Student could explain AI help: yes/no/unclear
Student could name what they verified: yes/no/unclear
Student could name human responsibility: yes/no/unclear
Confusion notes:
Next-run change:
```

Do not save student identity or raw private prompt in the research note.

## Success criteria

A session is useful if the student can say:

1. AI helped me with ____.
2. I verified ____.
3. I kept responsibility for ____.
4. Next time I will ask AI ____.

## Local scaffold

### Primary surface — open the web page

The intended student experience is the local web page:

```text
nous-os/demo/student-sandbox-v1.html
```

Open it directly in a browser (double-click, or `open demo/student-sandbox-v1.html`). It renders the 6 phases, source checklist, reflection card, and parent/teacher observation prompts as a single self-contained page. Nothing typed in the page is uploaded, saved to disk, or persisted across reloads — closing the tab discards everything.

### Student / parent why-and-how page

For students and parents who want context before opening the sandbox, the matching guide page is:

```text
nous-os/demo/student-sandbox-v1-guide.html
```

It explains why the sandbox exists, the five promises it keeps, what a session looks like for a student, a parent, and a teacher, and a step-by-step run-through. The sandbox page links to it from the top bar (`why & how`).

### Optional — regenerate the JSON artifact for research archival

If you also want a research-side record of the loop schedule:

```bash
cd /Users/liyao/nousos/nous-os
python3 examples/student_sandbox_v1.py --question "How should I research CRISPR ethics for biology class?"
```

This writes a local artifact under:

```text
examples/runtime/research-records/student-sandbox-v1-latest.json
```

The artifact is the same loop content the web page renders; the page is the human-facing surface, the JSON is for archival and contract testing. Both are local-only and do not call external models.
