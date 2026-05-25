# PROGRESS — JARVIS single source of truth

> **This file is the BRIDGE** between Claude Code (the builder, in this repo) and Rafael's
> separate planning chat on Claude.ai. Rafael manually carries it between them. **If anything
> conflicts with this file, the file wins.** Keep it lean, scannable, and self-contained — a
> fresh reader with zero other context must be able to act on it instantly.

---

## ⚡ TL;DR — paste-ready status
- **Phase:** Phase 0 ✅ done → **Phase 1 — Voice loop** (next)
- **Next action:** Phase 1 — implement the ElevenLabs voice loop in `main.py` and `pip install` `elevenlabs[pyaudio]` + `python-dotenv` into `./venv`. **Blocked until user finishes the unblock list below.**
- **Blocked on user:** real `.env` keys + ElevenLabs agent created in the dashboard. See "Next action — Build step" for details.
- **Last commit:** `f9ef8f8` — 2026-05-24 — `docs(progress): record Phase 0 done + self-improvement north star`.
- **Repo:** `C:\Users\Rafael\OneDrive\Área de Trabalho\Jarvis\` · branch `main`.

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
- **2026-05-24 — Phase 0 — Scaffold.** Project scaffolded at `C:\Users\Rafael\OneDrive\Área de Trabalho\Jarvis\` via the kickoff's alternative path (unzipped + flattened `starter/` → root). Python 3.13.13 `venv` created at `./venv` (no packages installed yet, per brief). `.env` populated with placeholders only — Rafael fills real keys. Two commits on `main`: `fae22be` (initial scaffold) and `f9ef8f8` (this PROGRESS.md update + north-star directive logged).

---

## 🔧 Known issues / WIP
- **Python is 3.13.13 here, not 3.11** (docs assume 3.11+). If `pip install -r requirements.txt` fails in Phase 1, paste the full error — fallback is pinning compatible versions or rebuilding the venv with Python 3.11/3.12.
- **Git identity is repo-local only** (`rafaelxoliver4@gmail.com` / `Rafael` in `.git/config`), not global. Change inside the Jarvis folder if a different name on commits is preferred.
- **OneDrive sync** sometimes locks files during heavy operations (venv writes, `pip install`). If you hit a weird file-lock error, pause OneDrive sync for a minute and retry.

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

## 🗺️ Phase roadmap (the build)
- **Phase 0** ✅ Scaffold
- **Phase 1** ⏭️ Voice loop (no tools) — `main.py` + ElevenLabs Conversation
- **Phase 2** First real tool: `open_application` (learn the pattern)
- **Phase 3** Core tools: `search_web`, `save_file`, `create_html_file`, `get_system_info`, `control_window`
- **Phase 4** Browser control: `browse(task)` via Playwright/MCP
- **Phase 5** ⭐ Reasoning & delegation: `delegate_task` via Claude Agent SDK
- **Phase 6** ⭐ Persistent memory: `remember`/`recall`, loaded at session start
- **NEW Phase 6.5** ⭐ **Self-improvement loop:** after every `delegate_task`, write a structured "what worked / what didn't / what I learned" note into `memory/`; future delegations include the relevant notes in the system prompt. **This is the feature that delivers the north star.**
- **Phase 7** Polish: wake word, screen vision, startup launch, tool log, tool router

⭐ = directly serves the "JARVIS improves itself the more we use it" directive.

> **Suggested order tweak (logged 2026-05-24):** the original build guide does Phase 4 (browser) before Phase 5 (delegation) and Phase 6 (memory). For Rafael's north-star goal, we'd flip that — `1 → 2 → 3 → 5 → 6 → 6.5 → 4 → 7` — so the compounding-knowledge features land before the one-shot capability bumps. Awaiting Rafael's call from the planning chat.

---

## 🧠 Decision log (newest first)
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
  - Tool usage log — track which tools fire and outcomes; surface unused/broken tools for review.
  - Vector-store semantic memory upgrade from JSON (Chroma or similar).
- Calendar + email (draft-only) via APIs or MCP servers.
- Multi-agent orchestration (specialised research / email / calendar sub-agents under one Jarvis).
- Proactive / scheduled tasks (morning briefing, reminders, background work overnight).
- Tool router once we exceed ~15–20 tools (avoid context rot from too many visible tools).
- Smart-home integrations (if compatible hardware).
