# Student Sandbox v1 Trial Recruitment Templates

Short, copy-paste-ready messages for inviting one parent or one teacher to a 20-minute Student Sandbox v1 trial. Pick a variant, fill the `<URL>` slot, send it. The variants are intentionally short and free of marketing.

## Before you send

- The `<URL>` slot should point at the **Why &amp; How** route (`/demo/student-sandbox-v1-guide.html`), not the sandbox route directly. Adults need the context first.
- If you have not deployed it, run `nous-os serve web --profile student` and share `http://<your-ip>:8787/demo/student-sandbox-v1-guide.html` on the same network. **Don't promise a public URL you don't have.**
- The sandbox page and the guide page are both in English. If your recruit is more comfortable in Chinese, send the Chinese message but flag that the page is currently English-only — don't ambush them.
- Never include the student's name, school name, or any identifying detail in the recruitment message itself.

---

## For a parent — 中文

> 我在试一个开源的 AI 学习沙盒（NOUS OS Student Sandbox v1），20 分钟一次，本地运行，不联网，不收姓名、学校、邮箱，不替学生写作业，关闭标签页后所有输入都丢弃。
>
> 它的设计核心是"AI 只给提示，不给答案"——孩子自己提问、自己设边界、自己挑两个来源做核对、最后写四句反思。我想找一个高中阶段的学生陪我跑一次，全程 20 分钟，加上 5 分钟我做旁观记录。
>
> 你们愿意试试吗？想先看页面也可以，先打开这个介绍：`<URL>`。（页面目前是英文的。）

## For a parent — English

> I'm trying out an open-source AI learning sandbox (NOUS OS Student Sandbox v1). It's a 20-minute scaffold that runs entirely in the browser — no login, no upload, no account, nothing saved. The whole point is that AI only gives hints, never final answers; the student frames the question, sets one boundary, checks two sources, and writes a short reflection.
>
> Would you and one high-school-age student be willing to try one 20-minute session? I'd sit nearby and take observation notes (no identifying details recorded). The "why and how" page is here: `<URL>`.

---

## For a teacher — 中文

> 我在试一个 20 分钟的 AI 研究学习循环（开源、本地运行、不上传任何数据），想找一位愿意旁观的老师做一次试用观察。
>
> 它不是 AI 替学生写作业的工具——刚好相反，整个流程逼着学生自己提问、设一个 AI 不可越界的限制、做两个来源核对、最后回答四个反思问题（"AI 帮了什么/我验证了什么/我留着的责任/下次怎么问"）。
>
> 你看一眼介绍页（`<URL>`），如果愿意试一次，告诉我哪个时间方便。整个过程 25 分钟以内。

## For a teacher — English

> I'm piloting a 20-minute AI-assisted research scaffold (open source, local-only, no data leaves the browser) and looking for one teacher willing to sit in on a trial session.
>
> It's not an AI-writes-the-homework tool — the opposite: the student frames the question, sets one explicit boundary AI is not allowed to cross, checks two sources, and ends with four reflection prompts ("What did AI help with? What did I verify? What remains my responsibility? What would I ask differently next time?").
>
> Skim the why-and-how page (`<URL>`) and tell me a 25-minute window if it looks worth trying.

---

## What not to promise

When tweaking these templates, do not add language that the page does not actually deliver. Specifically:

- Do **not** call this a "personalized AI tutor" — the page never calls an AI itself.
- Do **not** promise saved progress, login, or any record of the student's session — none of that exists.
- Do **not** promise a grade, score, or comparison — none of that exists.
- Do **not** promise the page will help with a specific assignment or rubric — it teaches the loop, not the answer.
- Do **not** include the student's identifying information in the message; talk in topic areas, not specifics.

## After the session

Use [[Student Sandbox v1 Trial Review Template]] in the Obsidian `04 Reviews/` folder, or the repo source-of-truth at `docs/student-sandbox-v1-review-template.md`. The trial review is a process review, not a student evaluation.
