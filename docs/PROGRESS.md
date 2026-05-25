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
- **Python decision:** rebuild `venv` against Anaconda's 3.12.4 at Phase 1 start (3.13 is currently in the venv but will be replaced).
- **Repo:** `C:\Users\Rafael\OneDrive\Área de Trabalho\Jarvis\` · branch `main` · run `git log --oneline` for the commit trail.
- **Open questions blocking acceleration:** 7 strategic decisions queued for the planning chat — see "Open questions" section below.

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

## ❓ Open questions for the planning chat
These are queued for Rafael's planning chat to decide. When a question is answered, move it to the Decision log (newest-first) with the date and rationale. **Phase 1 is not actually blocked by these** — they only need to be answered before the phases they affect.

1. **Phase order.** Original brief: `1 → 2 → 3 → 4 → 5 → 6 → 7`. Claude Code suggests `1 → 2 → 3 → 5 → 6 → 6.5 → 4 → 7` so the compounding-knowledge features (delegation + memory + self-reflection) land before the browser. **Confirm or reject.** *Affects: phase ordering from Phase 4 onward.*

2. **Phase 6.5 self-reflection schema.** After every `delegate_task`, JARVIS writes a structured note into `memory/` that future delegations include in their system prompt. **What fields should the note carry?** Strawman to react to:
   ```json
   {
     "date": "ISO 8601",
     "goal": "user's original ask, one sentence",
     "plan_summary": "what JARVIS decided to do",
     "tools_used": ["list", "of", "tool", "names"],
     "outcome": "succeeded | partial | failed",
     "surprises_or_errors": "anything unexpected — short",
     "advice_for_future_self": "1-2 sentences future-JARVIS should see when tackling similar goals"
   }
   ```
   This is the load-bearing format for the north star. Worth careful thought. *Affects: Phase 6.5.*

3. **Memory v1 file format** (Phase 6). JSON-lines? Single JSON dict? Markdown notes with YAML frontmatter (Obsidian-style — Rafael already lives in Obsidian, so this could double as wiki content)? Eventually a Chroma vector store, but v1 picks one. *Affects: Phase 6.*

4. **`delegate_task` dashboard registration timing.** It's a stub now (returns "I can't do that yet"). Register in the ElevenLabs dashboard now so Jarvis can apologise gracefully on multi-step asks, or wait until Phase 5 so Jarvis never tries to call it? *Affects: dashboard config, behaviour on first multi-step request.*

5. **Pre-Phase-2 tool log detour.** ~5-min addition: `logs/usage_log.jsonl` + a `wrap_log()` helper every tool wraps with. Records every tool call from day one, so when we hit Phase 6.5 we already have months of telemetry to learn from. **Add between Phase 1 and Phase 2, or defer to Phase 7?** Strong case for adding now — retrofitting later is more work and we lose all historical telemetry. *Affects: Phase 1.5 (new) vs. Phase 7.*

6. **Browser control approach** (Phase 4). Playwright (we control fully, more code) vs. an MCP browser server (less code, less control, depends on a third party). Lock in before Phase 4 so we don't burn a session researching. *Affects: Phase 4.*

7. **Wake word** (Phase 7). Porcupine (commercial), OpenWakeWord (open source), or skip entirely and use push-to-talk? *Affects: Phase 7.*

---

## 🧠 Decision log (newest first)
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
  - Tool usage log — track which tools fire and outcomes; surface unused/broken tools for review.
  - Vector-store semantic memory upgrade from JSON (Chroma or similar).
- Calendar + email (draft-only) via APIs or MCP servers.
- Multi-agent orchestration (specialised research / email / calendar sub-agents under one Jarvis).
- Proactive / scheduled tasks (morning briefing, reminders, background work overnight).
- Tool router once we exceed ~15–20 tools (avoid context rot from too many visible tools).
- Smart-home integrations (if compatible hardware).
