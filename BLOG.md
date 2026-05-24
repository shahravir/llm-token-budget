# Token Budget Discipline: A Developer's Playbook for the Quota Era

*You opened Claude Desktop, asked Opus 4.7 to polish three slides, and four hours later your entire afternoon quota is gone. Sound familiar?*

Every major LLM surface you touch—**Claude Desktop**, **Claude Code**, **ChatGPT**, **GitHub Copilot**, **Cursor**—now meters your work in tokens, messages, or opaque “usage limits.” The rules differ per product, but the pain is the same: you burn through budget on a small task, then sit in a **4–5 hour cooldown** while a large migration, PR review, or incident response still needs GenAI.

This is not an enterprise architecture problem. It is a **developer workflow** problem. The fix is not “buy more seats.” It is learning to treat tokens like CPU, memory, or CI minutes: a scarce resource you **budget, monitor, and route**.

---

## The new constraint: quota is the API

| Surface | How quota often feels | Typical developer pain |
|--------|------------------------|---------------------------|
| **Claude Desktop** | Session / model-tier caps; Opus burns fast | One “small” creative task empties hours of budget |
| **Claude Code** | Usage tied to plan + model | Long agent sessions on big repos |
| **ChatGPT** | Message caps, model gating (Plus/Pro/Team) | Switching models mid-task; team pool exhaustion |
| **GitHub Copilot** | Premium requests, agent mode limits | Agent loops on wide diffs |
| **Cursor** | Fast vs slow requests, model-specific pools | Composer + long context on monorepos |

Providers rarely expose a single “tokens remaining” dial you can trust across tools. What you *can* control is **what you send**, **which model reads it**, and **when you escalate** to a frontier model.

Think of this as **token budget discipline** (not “token anxiety”): deliberate choices so GenAI stays available when it matters.

---

## A real failure mode: the “three slides” incident

You are not imagining it. Frontier models on desktop UIs are optimized for quality and long context—not for frugality. A request like “turn these bullets into three executive slides” can pull in:

- Your pasted notes (large)
- Implicit style / brand instructions (re-sent every turn)
- Multiple revision rounds (each re-sends growing history)
- High reasoning depth on Opus-class models

**Result:** quota gone for ~5 hours; migration work continues **without** AI for the rest of the afternoon.

Scale that to a team: ten developers on a **Strangler Fig migration** all run agent mode against the same monorepo. By 11am, half the team is on manual refactor while deadlines do not move. That is **quota bankruptcy**—and it is operational, not theoretical.

---

## Principle 1: Context engineering is how you spend less

Prompt tricks alone will not save you. **Context engineering** is the discipline of putting *only the right information* in the window for *this* step—compression, selection, isolation, and external memory.

I wrote a deeper pattern catalog here:

- **Medium:** [Patterns for Context Engineering in Agentic Applications](https://medium.com/@shah.ravir) *(see your profile feed for the latest permalink)*
- **LinkedIn (full article):** [Patterns for Context Engineering in Agentic Applications](https://www.linkedin.com/pulse/patterns-context-engineering-agentic-applications-ravi-shah-uja4e)

**Read that article when you want the “why” and the eight patterns.** This post focuses on **day-to-day developer tactics** that implement those ideas without a platform team.

**Quick mapping:**

| Pattern (from the article) | Developer action |
|---------------------------|------------------|
| Context compression | Summarize logs/diffs before asking; never paste full CI output |
| Hierarchical context | Send file tree + signatures first; full files on demand |
| Semantic chunking | One concern per chat thread |
| External memory | `NOTES.md`, ADRs, scratchpads the agent reads selectively |
| Progressive disclosure | Index → retrieve → act (see sample `04-progressive-disclosure`) |
| Context rotation | New session per subtask; link prior summary in one paragraph |
| Differential context | “Since last turn, only these files changed: …” |

---

## Principle 2: Model routing—right brain, right price

Not every task deserves Opus, GPT-4.1, or Cursor’s heaviest model.

| Task type | Prefer | Avoid |
|-----------|--------|--------|
| Rename, boilerplate, regex fix | Fast / mini / Haiku / local 7–8B | Opus |
| Single-file bug with stack trace | Mid-tier + tight context | Whole-repo @-mention |
| Architecture, subtle concurrency | Frontier model + **small** curated context | Frontier + entire monorepo |
| Test generation from spec | Mid-tier | Multi-turn debate |
| Security-sensitive review | Dedicated pass, frozen diff | Rolling chat with stale files |

**Rule:** *Escalate the model only after you have escalated the quality of the context.*

Sample: [`samples/02-model-router`](samples/02-model-router) — a tiny Python router that picks `local` / `mid` / `frontier` from task metadata.

---

## Principle 3: Local LLMs for “token-free” grunt work

Your laptop (or a team GPU VM) can absorb work that does not need frontier reasoning:

- Commit message drafts from `git diff --stat`
- JSON/YAML formatting, enum extraction, comment cleanup
- First-pass unit test stubs from function signatures
- Grep-and-explain on a single file

**Ollama** (you likely already have `~/.ollama`) is enough for many teams:

```bash
ollama pull qwen2.5-coder:7b
ollama run qwen2.5-coder:7b
```

For **shared team use**, run a medium model on a small cloud GPU (L4, A10) behind an OpenAI-compatible proxy so everyone hits one endpoint—not five separate laptop quotas.

Sample: [`samples/05-local-ollama-router`](samples/05-local-ollama-router) — route “small” tasks to Ollama, escalate only on `confidence: low` or explicit flag.

**Honest limits:** local models hallucinate on cross-file refactors. Use them for **narrow, verifiable** tasks; keep frontier budget for integration and design.

---

## Principle 4: Skills and compressed modes (e.g. Caveman, Cavecrew)

Agent products re-send **system prompts, tool definitions, and memory** every turn. Custom **skills** (Cursor, Claude Code, Codex) let you pack recurring instructions once, in a dense form.

Two patterns I use:

1. **Caveman / compressed communication skills** — instruct the model to drop filler while keeping technical precision (~50–75% fewer output tokens on explanations). See [`skills/caveman-lite/SKILL.md`](skills/caveman-lite/SKILL.md).
2. **Cavecrew-style delegation** — spawn subagents (investigator / builder / reviewer) that return **file:line compressed** results so the main session context does not fill with prose.

**Developer habit:** maintain a `SKILL.md` per repo for “how we work here” (build, test, lint, forbidden paths) instead of pasting it into every chat.

Sample: [`samples/06-compressed-delegation`](samples/06-compressed-delegation) — investigator-style response formatter.

---

## Principle 5: Progressive disclosure in the IDE

The worst token spend is **@-mentioning the repo** or enabling “full codebase” for a one-line fix.

**Better workflow:**

1. Ask for a **map** (tree, symbols, routes) — cheap.
2. Agent **reads 1–3 files** — medium.
3. Frontier model **only** for the patch plan or tricky logic — expensive.

Sample: [`samples/04-progressive-disclosure`](samples/04-progressive-disclosure) — index builder + selective file load.

---

## Principle 6: Session hygiene developers actually follow

- **One job per chat** — “fix OAuth refresh” not “fix OAuth and refactor billing and update README.”
- **Checkpoint summaries** — every ~10 turns, ask: *“Summarize decisions in ≤15 bullets; I’ll start a new session.”* Paste only that summary forward.
- **Freeze the diff** — for reviews, attach `git diff main...HEAD` once, not live-updating files.
- **Close the loop in the terminal** — run tests/lint locally; paste **failures only**, not full green logs.
- **`.cursorignore` / `.claudeignore`** — exclude `node_modules`, build artifacts, lockfiles, generated protos.
- **MCP sparingly** — each tool schema costs context; enable tools you will use this session.

---

## Principle 7: Monitor what you can (even when vendors hide the meter)

You will not always get real-time token dashboards. Still:

| Signal | What to track |
|--------|----------------|
| Vendor UI | Usage %, reset time, model-specific pools |
| **Your** logs | Input chars, estimated tokens, model id per request |
| Session | Turns per task, files attached per turn |
| Team | Who burned quota before standup (shared pool products) |

Sample: [`samples/03-token-monitor`](samples/03-token-monitor) — wrap API calls with `tiktoken` estimates and CSV logging.

**Budget guardrails (personal or team):**

- Daily soft cap (e.g. 200k tokens frontier-equivalent)
- Alert at 70% before the big afternoon migration block
- **Reserve rule:** no Opus before 3pm unless incident severity = high

---

## Principle 8: Team patterns without a platform team

You do not need a central “AI platform” to avoid collective bankruptcy:

1. **Shared mid-tier endpoint** — one `qwen2.5-coder:32b` or similar on a team GPU; OpenAI-compatible API.
2. **Repo context pack** — committed `AGENTS.md` + skills; stops everyone re-explaining the monorepo.
3. **Migration playbook** — phases: inventory (local/mid) → plan (frontier, small context) → execute (mid + tight files) → review (frontier, diff only).
4. **Quota rota** — on heavy days, name one “frontier holder” for unblock; others stay on mid/local.
5. **Post-incident quota retro** — “What burned 40% of the pool?” beats guessing.

---

## Principle 9: Do more with less—tactical checklist

Before you hit Enter on the next prompt:

- [ ] Can a **local 7B** do this with a 50-line snippet?
- [ ] Did I **remove** stack traces, lockfiles, and binaries from context?
- [ ] Is this a **new session** instead of a 40-turn thread?
- [ ] Am I on the **smallest** model that can fail safely?
- [ ] Did I attach **only changed files**?
- [ ] Will I **verify in CI/tests** instead of asking the model to “run mentally”?
- [ ] For agents: did I set **scope** (“touch only `pkg/auth/`”)?
- [ ] Can a **skill** replace three paragraphs of instructions?

---

## When you are quota-blocked: a 5-hour survival kit

1. **Local model** — stubs, docs, commit messages, exploratory questions.
2. **Offline tools** — `rg`, `ast-grep`, IDE refactor, Copilot inline if still available on a different pool.
3. **Write for your future self** — update `AGENTS.md` with what you learned; tomorrow’s session starts cheaper.
4. **Batch frontier work** — queue 3–5 questions; one Opus session with prepared context beats five reactive chats.
5. **Human pairing** — quota bankruptcy is a signal to pair, not to pretend you do not need help.

---

## Sample code (companion repo)

Runnable examples for this article live in:

**[github.com/shahravir/llm-token-budget](https://github.com/shahravir/llm-token-budget)**

| Sample | Purpose |
|--------|---------|
| [`01-context-budget`](samples/01-context-budget) | Trim and prioritize context under a token ceiling |
| [`02-model-router`](samples/02-model-router) | Route tasks to local / mid / frontier |
| [`03-token-monitor`](samples/03-token-monitor) | Estimate and log token usage per call |
| [`04-progressive-disclosure`](samples/04-progressive-disclosure) | Build repo index; load files on demand |
| [`05-local-ollama-router`](samples/05-local-ollama-router) | Ollama-first with escalation hook |
| [`06-compressed-delegation`](samples/06-compressed-delegation) | Compressed subagent-style findings |

```bash
git clone https://github.com/shahravir/llm-token-budget.git
cd llm-token-budget
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

---

## Closing thought

GenAI availability is now a **non-functional requirement** of your development environment—like bandwidth or build queue time. Developers who treat tokens as infinite will keep losing afternoons to cooldown screens. Developers who practice **token budget discipline**—context engineering, model routing, local fallbacks, skills, and monitoring—will still hit limits, but on their own schedule, for work that actually needs frontier models.

**Go deeper on context:** [Patterns for Context Engineering in Agentic Applications](https://www.linkedin.com/pulse/patterns-context-engineering-agentic-applications-ravi-shah-uja4e)  
**Go deeper on code:** [shahravir/llm-token-budget](https://github.com/shahravir/llm-token-budget)

---

*Ravi Shah · [shahravir.github.io](https://shahravir.github.io) · [Medium @shah.ravir](https://medium.com/@shah.ravir)*
