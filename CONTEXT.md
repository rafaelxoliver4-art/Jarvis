# CONTEXT — JARVIS project briefing for new sessions

> **Read this BEFORE anything else.** This file is the "from scratch" briefing
> for any new conversation — whether you're a Claude Code session opening this
> repo, or a Claude.ai planning chat receiving a context upload. It captures
> what we're building, how we work, and what we've learned, so a new session
> can pick up exactly where the project left off without reconstructing the
> mental model from scratch.
>
> **For Rafael:** upload this file (or paste its contents) at the start of every
> new conversation with either Claude — Claude Code OR the planning chat. Pair
> it with `docs/PROGRESS.md` (the current state) so the new conversation has
> both the project's durable knowledge (this file) and its current TODO
> (PROGRESS.md).

---

## 1. What we're building

**JARVIS** is a voice-controlled agentic personal assistant running on Rafael's
Windows machine. You speak; it understands; it *does things* — opens apps,
creates files, searches the web, eventually browses, remembers, and delegates
multi-step tasks autonomously.

It is **not** a chatbot that describes how to do something. It's an agent with
hands — concrete actions on a real computer, guarded by structural safety
rules.

### Three-layer architecture (foundational mental model)

1. **ElevenLabs Agents (cloud)** — speech-to-text, text-to-speech (the Jarvis
   voice), and turn-taking. The hard speech machinery, hosted for us.
2. **A Claude model (brain, set in the ElevenLabs dashboard)** — understands
   intent and decides *which tool to call* with *what arguments*.
3. **Local Python "client tools" (hands)** — in `tools.py`, functions that
   actually do things on the machine. **This is where we add capability** —
   most "make Jarvis do more" work is just adding small, safe tools here.

Plus a fourth, special layer (Phase 5): **`delegate_task`** — for multi-step
autonomous jobs. This tool spawns a **Claude Agent SDK** loop that plans and
executes many steps, then returns a summary.

### ⭐ North star (immutable, user directive 2026-05-24)

*"JARVIS must keep improving itself the more we use it."*

Persistent memory, procedural skills, and post-task self-reflection are
load-bearing — not nice-to-haves. When picking what to build next, **prefer
features that compound knowledge over one-shot capabilities.**

### Where the project is (high level — read PROGRESS.md for detail)

```
Phase 0    ✅ Scaffold
Phase 1    ✅ Voice loop (main.py + ElevenLabs Conversation)
Phase 1.5  ✅ Tool-usage log (wrap_log + logs/usage_log.jsonl)
Phase 2    ✅ First real tool: open_application
Phase 3    🔧 IN PROGRESS — Core tools, one at a time
           ✅ get_system_info, ✅ save_file, ✅ create_html_file,
           🔧 search_web (current), control_window (after)
Phase 5    ⭐ Reasoning & delegation (delegate_task via Claude Agent SDK)
Phase 6    ⭐ Persistent memory (remember / recall)
Phase 6.5  ⭐ Self-improvement loop (procedural memory, NOT runtime self-mod)
Phase 4    Browser control (Playwright/MCP, deferred per north-star reorder)
Phase 7    Polish (push-to-talk first; wake word deferred)
```

⭐ = directly serves the self-improvement north star.

---

## 2. How we work — the operating model

This project is built by a **two-Claude team with Rafael as the human bridge:**

- **Planning chat** (Claude.ai project, separate from this code session) =
  **architect.** Researches, designs features, weighs decisions, writes the
  build prompts Rafael pastes into Claude Code.
- **Claude Code** (in this repo) = **builder.** Implements, runs, debugs,
  commits.
- **Rafael** = **bridge + human-in-the-loop.** Carries `docs/PROGRESS.md`
  between the two Claudes. Does the human-only steps: creating accounts,
  handling API keys, the ElevenLabs dashboard, running commands, voice
  testing, final approval calls.

The two Claudes **cannot talk directly.** Rafael manually carries
`docs/PROGRESS.md` between them. **If anything ever conflicts with
PROGRESS.md, PROGRESS.md wins.**

### Workflow per session

1. **START** — read `CLAUDE.md` and `docs/PROGRESS.md`. State the current
   phase and the single Next action.
2. **PLAN** — for any non-trivial change, propose a plan first; surface
   risks; wait for approval; then build.
3. **VERIFY** — after every change, *run / read / open* to confirm it
   worked. **"Done" requires evidence, not vibes.**
4. **END** — update `PROGRESS.md` (move finished items to Done, write the
   next single clear Next action, log decisions, note WIP/broken). Commit.
   **Never skip the wrap-up — treat omission as a failure.**

### Mutual vigilance

Two LLMs can compound mistakes — a plausible-but-wrong assumption from one
gets executed confidently by the other. Treat the planning chat's prompts
as a smart peer's *recommendations*, not commands — sanity-check each
against the current code, the architecture, and the safety rules. If a
prompt looks wrong, **flag it BEFORE building.** Full rules in `CLAUDE.md`
→ "Error-awareness & verification."

---

## 3. Standing conventions (lessons we forged, now baked in)

These were each learned from real test runs and bug-finds. Full context
for each lives in `docs/PROGRESS.md` → Decision log.

### Safety rules (NON-NEGOTIABLE)

- **File writes go ONLY into `./generated/`.** Use `_safe_path()` in
  `tools.py` — rejects `..`, `/`, `\`, absolute paths, escape attempts.
  Reuse it for any file-writing tool.
- **App / window / system actions use ALLOW-LISTS.** Unknown target →
  polite refusal, no execution.
- **NO open-ended shell tool.** Voice + arbitrary shell = remote-code-exec
  risk.
- **Irreversible/sensitive actions** (delete, send, buy, submit form)
  RETURN a confirmation request — never execute directly.
- **Never read, print, log, or transmit `.env` values, secrets, or API
  keys.**
- **`delegate_task` (Phase 5)** must run with hard `max_turns` + timeout +
  allow-listed tools only.

### The per-tool build pattern (standing loop)

For every new tool from Phase 2 onward:

1. *(if needed)* `pip install` + pin the dep in `requirements.txt`
2. Write the function in `tools.py` — takes a single `parameters` dict,
   returns a short voice-friendly string, follows the Safety rules
3. **Wrap with `wrap_log()` at registration** (every tool is auto-logged
   to `logs/usage_log.jsonl`)
4. Verify imports clean: `python -c "import tools; print(type(tools.client_tools).__name__)"`
5. Run a **direct-invocation test** (bypass the ElevenLabs agent — exercises
   the code-layer safety; voice tests can be intercepted at the prompt
   layer and miss real bugs)
6. Hand off dashboard registration text to Rafael
7. After Rafael registers, orchestrate a 30s voice test
   (`python -u`, background timer, log-capture)
8. Rafael confirms the observable side-effect actually happened
9. Commit + update `PROGRESS.md`

### Dashboard configuration gotchas

- **"Wait for response" must be ENABLED for return-valued tools.** Without
  it, the cloud agent doesn't wait for the SDK's response and uses a
  fallback *"called successfully"* string → the agent says *"tool ran but
  no readable data."* Fire-and-forget tools (like `open_application`)
  correctly work with it OFF.
- **Response timeout defaults to 1 SECOND.** Bump for any tool slower than
  ~700ms. Standing recommendations: `save_file`=5s, `create_html_file`=5s,
  `search_web`=15s, future `delegate_task`=30s.
- **Zero-param tools are supported** — the dashboard accepts tools with no
  parameters; the SDK auto-injects `tool_call_id`. No dummy param needed.

### Code patterns

- **`python -u` (unbuffered stdout)** is required when orchestrating
  `main.py` from a non-interactive shell. Without it, prints get
  block-buffered and "JARVIS is listening" never appears in captured logs.
  For Rafael's own TTY runs this isn't needed.
- **`wrap_log` design contracts:** thread-safe (module-level
  `threading.Lock`); fail-open (logging errors swallowed); secrets-safe
  (substring redaction on params with key names matching `key`, `token`,
  `secret`, `password`, `passwd`, `api`, `auth`, `credential`); tool return
  values are NOT logged (privacy).
- **Multi-tool chaining works.** The LLM agent composes tools across
  multi-turn conversation and asks permission before consequential
  follow-ups. Confirmed live during Phase-3-Tool-#3.
- **Defense in depth.** A safety-test via voice may be intercepted by the
  prompt-layer (LLM refuses based on tool description) before reaching
  the code-layer. ALWAYS pair voice tests with direct-invocation tests
  for any tool with structural safety.

### Known bugs (tracked in `docs/PROGRESS.md` → WIP)

- **`open_application` silently lies on Windows** when an allow-list entry
  isn't a true Windows PATH builtin (`chrome`, `spotify`, `vscode`
  probably affected; `calc`/`notepad` work). `Popen(target, shell=True)`
  doesn't raise even when the shell can't find the exe — function returns
  "Opening …, sir." with wrap_log `outcome=ok` while nothing happens.
  Fix path: use `Popen(["cmd","/c","start","",target], shell=False)`
  (registry-aware). **Must fix before Phase 5** so autonomous loops
  can't be fooled by silent "success."

### Tooling / dependency lessons

- **Use `ddgs` directly, NOT `langchain-community`.** During Phase-3
  Tool-#4, we discovered `langchain-community` is being sunset (per its
  own deprecation warning) and unbundled its `duckduckgo-search` dep
  (renamed `ddgs`). Going directly to `ddgs` gives us 1 dep instead of
  28, no deprecation, and structured results (`title`, `href`, `body`)
  we format ourselves. **Standing rule:** when a future tool needs a
  capability, prefer the direct library over a meta-package wrapper.

---

## 4. Doc map — where to look for what

| Need to know... | Read |
|---|---|
| **The "read first" briefing (this file)** | **`CONTEXT.md`** |
| **Current state, next action, recent decisions** | **`docs/PROGRESS.md`** |
| The rules of how Claude Code operates | `CLAUDE.md` |
| The project vision + capability roadmap | `README.md`, `docs/CAPABILITIES.md` |
| The technical architecture in depth | `docs/ARCHITECTURE.md` |
| Phased build prompts to paste into Claude Code | `docs/BUILD_GUIDE.md` |
| Reusable prompts (Jarvis system prompt, debug template) | `docs/PROMPT_LIBRARY.md` |
| The actual code | `tools.py` (capabilities), `tool_logging.py` (telemetry), `main.py` (voice loop wiring) |
| Persistent memory / self-improvement | `memory/` (added Phase 6), `agents/` (added Phase 5) |
| The original kickoff brief (historical) | `JARVIS_KICKOFF.md` |

---

## 5. For Rafael — how to use this file across sessions

Treat `CONTEXT.md` as the **first thing you upload** to any new Claude
conversation about JARVIS:

- **For Claude Code in this repo:** the agent reads it automatically because
  `CLAUDE.md` references it in the session-start ritual.
- **For your planning chat (Claude.ai):** upload alongside `docs/PROGRESS.md`.
  CONTEXT gives the planning chat the durable knowledge of how we work and
  what we've learned; PROGRESS gives it the current state and Next action.
  Together they let any fresh planning-chat conversation hit the ground
  running.
- **For ad-hoc Claude conversations** (e.g. you have a quick question
  outside the main flow): upload CONTEXT.md and the relevant file (a tool
  source, a log file, etc.). Skip PROGRESS.md if it's not state-relevant.

### When to update this file

The natural cadence is: **after a phase wraps + a meaningful learning has
landed.** Not for tiny changes (those go in PROGRESS.md), but for:

- A new foundational rule we discovered (e.g. *"Wait for response" must be
  on for return-valued tools*).
- A bug class with a permanent lesson (e.g. *Windows shell launches don't
  raise on missing exe*).
- A standing convention that future tools should follow.
- An architectural decision that future Claude sessions need to know.

When PROGRESS.md's Decision log gets a new entry that *should outlive the
current phase*, mirror its essence here.

---

## 6. Update history

- **2026-05-26** — Created during Phase 3 Tool #4 (`search_web`) build.
  Consolidates conventions and learnings from Phases 0 through Phase 3
  Tool #4. Idea: Rafael wanted a durable "from scratch" briefing that
  works for both Claude Code AND the Claude.ai planning chat, separate
  from PROGRESS.md (which is state-only and updates session-by-session).
