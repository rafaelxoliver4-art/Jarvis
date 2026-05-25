# PROGRESS — the project's living memory

> This is the **baton** passed between every work session. Claude Code reads it at session start
> and updates it at session end (see the ritual in `CLAUDE.md`). When in doubt about where the
> project is, read THIS file first.

---

## 📍 Current phase
**Phase 0 — Scaffold** ✅ done. Ready for **Phase 1 — Voice loop** (blocked on user setup, see below).

## ⏭️ Next action (do this next — keep it to ONE clear step)
**Phase 1 — Voice loop.** Before pasting the Phase 1 prompt into Claude Code, the user must:
1. Fill `Jarvis/.env` with real `ELEVENLABS_API_KEY` and `AGENT_ID` (never let an assistant touch keys).
2. In the **ElevenLabs dashboard**: create an Agent → set its LLM to a **Claude** model → paste the
   Jarvis system prompt from `docs/PROMPT_LIBRARY.md` → pick the "Charlie"-style voice → copy the
   Agent ID into `.env`.

Once `.env` is real, paste the **Phase 1 — Voice loop** prompt from `docs/BUILD_GUIDE.md` into Claude
Code. It installs `elevenlabs[pyaudio]` + `python-dotenv`, wires up `Conversation` in `main.py`, and
tests the talking loop end-to-end (no tools yet).

---

## ✅ Done
- **2026-05-24** — Phase 0 scaffold complete. Project lives at
  `C:\Users\Rafael\OneDrive\Área de Trabalho\Jarvis\`. Created via the kickoff alternative path
  (unzipped + flattened starter/ → root). Venv created at `Jarvis/venv` (Python 3.13.13, no packages
  installed yet). `.env` populated with placeholders only. First git commit `fae22be`.

## 🔧 Known issues / work-in-progress
- **Python version is 3.13.13, not 3.11 as the docs suggest.** Some pinned-old packages may
  complain at install time. Mitigation: if `pip install -r requirements.txt` fails in Phase 1, paste
  the full error and we'll either pin compatible versions or fall back to a Python 3.11/3.12 venv.
- **Git identity is repo-local only** (`rafaelxoliver4@gmail.com` / `Rafael`), not global. Change
  with `git config user.name "..."` / `user.email "..."` inside the Jarvis folder if desired.

## 🧩 Tools built & dashboard registration status
| Tool | In code? | Registered in ElevenLabs dashboard? |
|------|----------|--------------------------------------|
| `open_application` | ✅ (skeleton, allow-list of 5 apps) | ❌ — register in Phase 2 |
| `save_file`        | ✅ (skeleton, `./generated/` sandbox) | ❌ — register in Phase 3 |
| `delegate_task`    | ⚠️ stub only — full impl in Phase 5 | ❌ — register in Phase 5 |

> Note: the skeletons from `tools.py` exist but are NOT yet exposed end-to-end — Phase 1 first
> proves the voice loop works without tools; Phase 2 is the first real round-trip
> (voice → tool → action).

## 🧠 Decision log (what we chose and why)
- **2026-05-24** — Brain LLM = a **Claude model** in the ElevenLabs dashboard (most reliable
  tool-calling, which is the whole point of an acting agent).
- **2026-05-24** — Reasoning/delegation via the **Claude Agent SDK** (`claude-agent-sdk`) rather
  than hand-rolling an agent loop — it's the same engine as Claude Code, as a library.
- **2026-05-24** — Safety is **structural** (allow-lists + `./generated/` sandbox in code), not
  just prompt-based, so a misheard command can't cause damage.
- **2026-05-24** — Browser control will use real automation (Playwright / MCP), not pixel-clicking.
- **2026-05-24 (NEW — user directive)** — ⭐ **JARVIS must keep improving itself the more it's
  used.** This is a north-star requirement. Persistent memory (Phase 6), procedural skills, and
  post-task self-reflection are not nice-to-haves — they're the point. When picking what to build
  next, prefer features that compound knowledge over one-shot capabilities.
- **2026-05-24** — `.gitignore` tweaked from `generated/` → `generated/*` + `!generated/.gitkeep` so
  the empty sandbox folder is tracked but user output written into it is not.
- **2026-05-24** — Git identity set **locally** (in `.git/config`), not globally — minimal blast
  radius; user can promote to global later if they want.

## 💡 Ideas / backlog (not scheduled yet)
- Calendar + email (draft-only) via APIs or MCP servers.
- Multi-agent orchestration (specialized research/email/calendar sub-agents).
- Proactive/scheduled tasks (morning briefing, reminders).
- Tool router once we exceed ~15–20 tools.
- Vector-store semantic memory upgrade.
- **Self-improvement loop (priority — flows from the north-star directive):**
  - After each `delegate_task` run, write a structured "what worked / what didn't / what I learned"
    note into `memory/`. Future delegations include relevant notes in the system prompt.
  - "Skill" library: capture repeatable recipes ("my morning standup prep") so they can be replayed.
  - Tool usage log: track which tools fire and outcomes, surface unused/broken tools for review.

---

### How to update this file (template for the wrap-up)
```
Current phase: <phase>
Next action: <one clear step>
Done: + <date> — <what completed>
Known issues / WIP: <anything half-finished or broken>
Tools table: <add row / flip registration status>
Decision log: + <date> — <decision + why> (only if a real decision was made)
```
