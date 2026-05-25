# PROGRESS — JARVIS single source of truth

> **This file is the BRIDGE** between Claude Code (the builder, in this repo) and Rafael's
> separate planning chat on Claude.ai. Rafael manually carries it between them. **If anything
> conflicts with this file, the file wins.** Keep it lean, scannable, and self-contained — a
> fresh reader with zero other context must be able to act on it instantly.

> Full operating model (who does what) lives in CLAUDE.md → Operating model.

> Mutual vigilance: both Claudes stay alert to each other's mistakes; nothing is 'done' until verified. Full rules in CLAUDE.md → Error-awareness & verification.

---

## ⚡ TL;DR — paste-ready status
- **Phase:** Phase 0 ✅ done → **Phase 1 — Voice loop** (next)
- **Next action:** Phase 1 — implement the ElevenLabs voice loop in `main.py` and `pip install` `elevenlabs[pyaudio]` + `python-dotenv` into `./venv`. **Blocked until user finishes the unblock list below.**
- **Blocked on user:** real `.env` keys + ElevenLabs agent created in the dashboard. See "Next action — Build step" for details.
- **Python decision:** rebuild `venv` against Anaconda's 3.12.4 at Phase 1 start (3.13 is currently in the venv but will be replaced).
- **Repo:** `C:\Users\Rafael\OneDrive\Área de Trabalho\Jarvis\` · branch `main` · run `git log --oneline` for the commit trail.
- **Open questions:** none — all 7 resolved by the planning chat 2026-05-25 (see Decision log).

---

## 🧭 What JARVIS is (elevator)
A voice-controlled agentic personal assistant that runs on Rafael's Windows machine. Three layers: **ElevenLabs Agents** (speech-in / speech-out / turn-taking, cloud) → **a Claude model set in the ElevenLabs dashboard** (the brain that picks tools) → **local Python "client tools"** in this repo (the hands that actually act). For multi-step jobs, one tool — `delegate_task` — hands off to a **Claude Agent SDK** loop. Read `docs/ARCHITECTURE.md` before any structural change.

**⭐ North star (user directive, 2026-05-24):** *"JARVIS must keep improving itself the more we use it."* Treat persistent memory, procedural skills, and post-task self-reflection as load-bearing — not nice-to-haves. When choosing what to build next, prefer features that compound knowledge over one-shot capabilities.

---

## ⏭️ Next action

### What Claude Code does next (Phase 1 — Voice loop)
Paste the **Phase 1 — Voice loop** prompt from `docs/BUILD_GUIDE.md` into Claude Code. Specifically:
1. Activate `./venv` and `pip install elevenlabs[pyaudio] python-dotenv` (re-pin if Python 3.13 chokes — see WIP).
2. Implement the ElevenLabs `Conversation` wiring in `main.py` per the current SDK docs (https://elevenlabs.io/docs/eleven-agents/libraries/python — fetch, don't guess).
3. Wire callbacks for agent response, user transcript, Ctrl+C → `end_session()`.
4. Test: run `python main.py`, say hello, Jarvis replies in voice. No tools yet.
5. Commit. Update this file (move Phase 1 to Done, set Phase 2 as next).

### What Rafael must finish first (UNBLOCK list)
- [ ] **ElevenLabs dashboard:** create an Agent → set its LLM to a **Claude** model → paste the Jarvis system prompt from `docs/PROMPT_LIBRARY.md` § A → pick a "Charlie"-style voice → copy the **Agent ID** and create an **API key**.
- [ ] **Anthropic API key** at console.anthropic.com (not strictly needed until Phase 5, but easier to drop in now).
- [ ] **Fill `Jarvis/.env`** with the real `ELEVENLABS_API_KEY`, `AGENT_ID`, `ANTHROPIC_API_KEY`. Never share these with Claude — Claude must never read, log, or transmit them.
- [ ] Mic + speakers working under Windows default capture/playback.

---

## ✅ Done
- **2026-05-24 — Phase 0 — Scaffold.** Project scaffolded at `C:\Users\Rafael\OneDrive\Área de Trabalho\Jarvis\` via the kickoff's alternative path (unzipped + flattened `starter/` → root). Python 3.13.13 `venv` created at `./venv` (no packages installed yet, per brief — will be rebuilt against 3.12 at Phase 1 start). `.env` populated with placeholders only — Rafael fills real keys.
- **2026-05-24 — Bridge convention encoded** in `CLAUDE.md` so future Claude Code sessions automatically inherit it (PROGRESS.md is single source of truth; file wins on conflicts; lean + scannable for zero-context readers; mandatory end-of-session ritual).
- **2026-05-24 — Python environment scan** completed: confirmed 3.12.4 (Anaconda) and 3.13.13 (Store) are the only Pythons available. No 3.11. Anaconda's interpreter is the chosen target for `venv`.

---

## 🔧 Known issues / WIP
- **🚧 Phase 1 build is BLOCKED** awaiting two human-only actions from Rafael: (1) create the ElevenLabs agent in the dashboard (set its LLM to a Claude model, paste the Jarvis system prompt from `docs/PROMPT_LIBRARY.md` § A), and (2) fill `Jarvis/.env` with the real `ELEVENLABS_API_KEY` + `AGENT_ID` (and `ANTHROPIC_API_KEY` if grabbing it now). Claude Code must NOT start implementing the voice loop before both are confirmed — building without a real agent to connect to would only stall or force guesses.
- **Jarvis/venv currently points at Python 3.13.13** (Microsoft Store install). At Phase 1 start, the **plan is to rebuild it against Python 3.12.4** (Anaconda at `C:\Users\Rafael\anaconda3\python.exe`) — 3.12 has the widest tested wheel coverage for `pyaudio`, `elevenlabs`, `langchain-community`, and `claude-agent-sdk`. 3.13 *probably* works but is newer than most of those libs' validation matrices.
- **Available Pythons on this machine** (verified 2026-05-24): 3.12.4 (Anaconda, recommended for Jarvis) and 3.13.13 (MS Store). No 3.11, no `py` launcher, no Visual C++ build tools — if a future package needs to build from source we'll need to install VC build tools.
- **Git identity is repo-local only** (`rafaelxoliver4@gmail.com` / `Rafael` in `.git/config`), not global. Change inside the Jarvis folder if a different name on commits is preferred.
- **OneDrive sync** sometimes locks files during heavy operations (venv writes, `pip install`). If you hit a weird file-lock error, pause OneDrive sync for a minute and retry. Right-click `Jarvis/` → "Always keep on this device" recommended to prevent offloading.

---

## 🧩 Tools — code & dashboard registration
A tool registered in code but NOT in the ElevenLabs dashboard is invisible to the agent. Both columns must be ✅ for a tool to actually work.

| Tool | In code? | In ElevenLabs dashboard? | Phase | Notes |
|---|---|---|---|---|
| `open_application` | ⚠️ skeleton in `tools.py` (allow-list: chrome, vscode, calculator, notes, spotify) | ❌ | Phase 2 | First end-to-end tool round-trip |
| `save_file`        | ⚠️ skeleton in `tools.py` (sandboxed to `./generated/`) | ❌ | Phase 3 | |
| `delegate_task`    | ⚠️ stub in `tools.py` — returns a "not built yet" message | ❌ | Phase 5 | Full impl via Claude Agent SDK; needs `max_turns` + timeout + allow-listed tools |
| `search_web`       | ⏳ not started | ❌ | Phase 3 | DuckDuckGo via `langchain-community` |
| `create_html_file` | ⏳ not started | ❌ | Phase 3 | Sandboxed |
| `get_system_info`  | ⏳ not started | ❌ | Phase 3 | `psutil`, read-only |
| `control_window`   | ⏳ not started | ❌ | Phase 3 | Allow-listed actions |
| `browse(task)`     | ⏳ not started | ❌ | Phase 4 | Playwright/MCP, not pixel-clicking |
| `remember` / `recall` | ⏳ not started | ❌ | Phase 6 | **North-star — load into context at session start** |

Legend: ✅ done · ⚠️ partial / skeleton only · ❌ missing · ⏳ not started yet

---

## 🗺️ Phase roadmap (the build — order confirmed 2026-05-25)
Build order: **`1 → 1.5 → 2 → 3 → 5 → 6 → 6.5 → 4 → 7`**. Compounding-knowledge features (delegation + memory + self-reflection) land before the browser.

- **Phase 0** ✅ Scaffold
- **Phase 1** ⏭️ Voice loop (no tools) — `main.py` + ElevenLabs Conversation
- **Phase 1.5** ⭐ **Tool-usage log** — `logs/usage_log.jsonl` + a `wrap_log()` helper every tool wraps with (timestamp, tool name, short param summary, outcome, duration). **Secrets-safe** — never log `.env` values or sensitive params. Done before Phase 2 so every real tool is logged from birth, giving Phase 6.5 full telemetry to learn from.
- **Phase 2** First real tool: `open_application` (learn the pattern)
- **Phase 3** Core tools: `search_web`, `save_file`, `create_html_file`, `get_system_info`, `control_window`
- **Phase 5** ⭐ Reasoning & delegation: `delegate_task` via Claude Agent SDK. Uses the SDK's built-in web search + file tools, so it's useful even before our `browse` tool exists; `browse` plugs into its allow-list later.
- **Phase 6** ⭐ Persistent memory: `remember`/`recall`, loaded at session start. **v1 store format = JSON Lines** (append-only `.jsonl`, one record per line, each tagged `type` = `"fact"` | `"reflection"`). Clean upgrade path to a Chroma vector store later.
- **Phase 6.5** ⭐ **Self-improvement loop** (procedural memory only — NOT runtime self-modification): after every `delegate_task`, write a structured reflection note; future delegations include relevant notes in the system prompt. Reflection-note schema (refinable at the phase): `{date (ISO 8601), tags[] (for retrieval), goal (one sentence), tools_used[], outcome (succeeded|partial|failed), what_helped, what_to_avoid, advice_for_future_self}`. **The feature that delivers the north star.**
- **Phase 4** Browser control: `browse(task)` — **provisional** lean toward Playwright (full control, mature, no third-party-MCP dependency); **re-validate at phase start** since the browser-automation landscape moves fast.
- **Phase 7** Polish: **push-to-talk first** (wake word deferred; if added later, lean OpenWakeWord over Porcupine), screen vision, startup launch, tool router

⭐ = directly serves the "JARVIS improves itself the more we use it" directive.

---

## ❓ Open questions for the planning chat
None currently — all resolved (see Decision log).

---

## 🧠 Decision log (newest first)
- **2026-05-25** — **Build order confirmed (Q1):** 1 → 1.5 → 2 → 3 → 5 → 6 → 6.5 → 4 → 7. Compounding-knowledge features (delegation, memory, self-reflection) land before the browser. Safe because delegate_task uses the Claude Agent SDK's built-in web search + file tools, so it's useful without our browse tool; browse plugs into its allow-list later.
- **2026-05-25** — **Tool-usage log = new Phase 1.5 (Q5):** right after the voice loop works, before the first real tool. Minimal logs/usage_log.jsonl + a wrap_log() helper every tool wraps with (timestamp, tool name, short param summary, outcome, duration). MUST be secrets-safe — never log .env values or sensitive params. Done before Phase 2 so every tool is logged from birth and Phase 6.5 has full telemetry; not before Phase 1 (no tools to log yet — prove the pipeline first).
- **2026-05-25** — **delegate_task stays UNREGISTERED in the dashboard until Phase 5 (Q4).** Registering a stub would make the agent call a dead tool; let it reason conversationally instead. Register only when it actually works.
- **2026-05-25** — **Phase 6.5 scoped to procedural memory only, NOT runtime self-modification (Q2).** JARVIS writes post-task reflection notes future runs read; it does NOT edit its own code/tools live (that stays a supervised Claude Code task Rafael approves). Reflection-note schema (refinable at Phase 6.5): {date (ISO 8601), tags[] (for retrieval), goal (one sentence), tools_used[], outcome (succeeded|partial|failed), what_helped, what_to_avoid, advice_for_future_self}. Added tags vs the strawman so recall can fetch relevant notes by task type.
- **2026-05-25** — **Memory v1 format = JSON Lines (Q3).** Append-only .jsonl, one record per line, each tagged type ("fact" | "reflection"). Simplest robust option, trivial to append/parse, clean upgrade path to a Chroma vector store. Obsidian/markdown dual-use deferred to a later "export memory to markdown" tool rather than making the primary store markdown.
- **2026-05-25** — **Browser approach = PROVISIONAL lean Playwright, finalize at Phase 4 (Q6).** Full control, mature, no third-party-MCP dependency, composes into delegate_task's allow-list. Marked provisional — re-run a fresh research pass at Phase 4 since the browser-automation/MCP landscape moves fast.
- **2026-05-25** — **Wake word deferred; start with push-to-talk (Q7).** Always-on wake word adds false-triggers and complexity for marginal early benefit. If added later, lean OpenWakeWord (open source) over Porcupine (commercial). Low-priority Phase 7.
- **2026-05-24** — **Jarvis/venv will be rebuilt against Anaconda's Python 3.12.4** at Phase 1 start. Rafael's machine has 3.12 (Anaconda) and 3.13 (MS Store) only; no 3.11. 3.12 is the safest target — widest tested-wheel coverage across `pyaudio`, `elevenlabs`, `langchain-community`, `claude-agent-sdk` — without installing anything new.
- **2026-05-24** — **PROGRESS.md is the manual BRIDGE to Rafael's planning chat** and the project's single source of truth. If anything conflicts with this file, the file wins. Convention encoded in `CLAUDE.md` and in Claude Code's user-level memory so it persists across sessions.
- **2026-05-24** — ⭐ **JARVIS must keep improving itself the more it's used** (user north-star directive). Persistent memory, procedural skills, and post-task self-reflection are load-bearing. Backlog and roadmap re-prioritised accordingly.
- **2026-05-24** — **`.gitignore` tweaked** from `generated/` → `generated/*` + `!generated/.gitkeep` so the empty sandbox folder is tracked but user output dropped into it isn't.
- **2026-05-24** — **Git identity scoped to this repo only**, not global — minimum blast radius; promotable to global later.
- **2026-05-24** — **Browser control will use Playwright / MCP** (real automation), not pixel-clicking, which breaks the moment the screen changes.
- **2026-05-24** — **Safety is structural** (allow-lists + `./generated/` sandbox in code), not just prompt-based — so a misheard command can't cause damage even if the prompt is ignored.
- **2026-05-24** — **Reasoning/delegation via the Claude Agent SDK** (`claude-agent-sdk`) rather than hand-rolling an agent loop — it's the same engine as Claude Code, exposed as a library.
- **2026-05-24** — **Brain LLM = a Claude model** in the ElevenLabs dashboard — most reliable tool-calling, which is the whole point of an acting agent.

---

## 💡 Backlog (not scheduled yet)
- **Self-improvement features (highest priority, flows from the north star):**
  - Skill library — capture repeatable recipes ("my morning standup prep") JARVIS can replay and refine.
  - Vector-store semantic memory upgrade from JSON Lines (Chroma or similar) — the Phase 6 v1 format is `.jsonl` with a clean upgrade path here.
- Calendar + email (draft-only) via APIs or MCP servers.
- Multi-agent orchestration (specialised research / email / calendar sub-agents under one Jarvis).
- Proactive / scheduled tasks (morning briefing, reminders, background work overnight).
- Tool router once we exceed ~15–20 tools (avoid context rot from too many visible tools).
- Smart-home integrations (if compatible hardware).
