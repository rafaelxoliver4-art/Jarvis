# PROGRESS — the project's living memory

> This is the **baton** passed between every work session. Claude Code reads it at session start
> and updates it at session end (see the ritual in `CLAUDE.md`). When in doubt about where the
> project is, read THIS file first.

---

## 📍 Current phase
**Phase 0 — Scaffold** (not started yet).

## ⏭️ Next action (do this next — keep it to ONE clear step)
Run the Phase 0 scaffold prompt from `docs/BUILD_GUIDE.md` in Claude Code, then create your real
`.env` from `.env.example`.

---

## ✅ Done
_(nothing yet — update with date as phases complete, e.g. "2026-05-24 — Phase 1 voice loop working")_

## 🔧 Known issues / work-in-progress
_(none yet)_

## 🧩 Tools built & dashboard registration status
| Tool | In code? | Registered in ElevenLabs dashboard? |
|------|----------|--------------------------------------|
| _(none yet)_ | | |

## 🧠 Decision log (what we chose and why)
- **2026-05-24** — Brain LLM = a **Claude model** in the ElevenLabs dashboard (most reliable
  tool-calling, which is the whole point of an acting agent).
- **2026-05-24** — Reasoning/delegation via the **Claude Agent SDK** (`claude-agent-sdk`) rather
  than hand-rolling an agent loop — it's the same engine as Claude Code, as a library.
- **2026-05-24** — Safety is **structural** (allow-lists + `./generated/` sandbox in code), not
  just prompt-based, so a misheard command can't cause damage.
- **2026-05-24** — Browser control will use real automation (Playwright / MCP), not pixel-clicking.

## 💡 Ideas / backlog (not scheduled yet)
- Calendar + email (draft-only) via APIs or MCP servers.
- Multi-agent orchestration (specialized research/email/calendar sub-agents).
- Proactive/scheduled tasks (morning briefing, reminders).
- Tool router once we exceed ~15–20 tools.
- Vector-store semantic memory upgrade.

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
