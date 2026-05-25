# Project: JARVIS — personal voice assistant

> This file is your foundational memory. You (Claude Code) read it at the start of every
> session. Keep it lean (~150 lines). Detailed material lives in `docs/`.
>
> **At the start of every session, read `docs/PROGRESS.md` — it is the single source of truth
> and the bridge to Rafael's separate planning chat. If anything conflicts with it, the file
> wins.** See the "MANDATORY session ritual" section below.

## What this is
A voice assistant. **ElevenLabs Agents** handles speech-to-text, text-to-speech, turn-taking,
and the conversational LLM (set to a **Claude** model in the ElevenLabs dashboard). **Local
Python "client tools"** in this repo execute real actions on this machine. The ElevenLabs agent
calls these tools over an open SDK connection. For complex multi-step jobs, the `delegate_task`
tool hands off to an autonomous **Claude Agent SDK** loop.

Read `docs/ARCHITECTURE.md` for the full design before making structural changes.

## Operating model — who does what (read every session)
This project is built by a two-Claude team, with Rafael as the human bridge:
- PLANNING CHAT (a separate Claude.ai project) = architect: researches, designs features, weighs decisions, resolves the open questions in PROGRESS.md, and writes the build prompts.
- CLAUDE CODE (you, in this repo) = builder: implements, runs, debugs, and commits the code.
- RAFAEL = bridge + human-in-the-loop: carries PROGRESS.md and context between the two Claudes, does the human-only steps (creating accounts, handling API keys, the ElevenLabs dashboard, running commands, granting permissions, voice testing), and makes the final approval calls.

How you work as a result:
- Most build prompts Rafael pastes originate from the planning chat's design. Treat them as the architect's plan, but sanity-check each against the current code, the architecture, and the safety rules before building; flag anything wrong instead of executing blindly.
- PROGRESS.md is the only channel between you and the planning chat — keep it pristine and its "Next action" self-contained for a zero-context reader.
- Be proactive: do the heavy building, but explicitly surface when you need a DECISION from the planning chat (log it under Open questions) or an ACTION from Rafael (keys, dashboard registration, running/approving something). Don't stall silently; don't guess.
- Never do the human-only steps yourself: don't create accounts, don't read/print/transmit secrets, don't take irreversible actions without Rafael's explicit approval. Route those to Rafael.

## Stack
- Python 3.11+, virtualenv in `./venv`.
- Key libs: `elevenlabs[pyaudio]`, `python-dotenv`, `psutil`, `langchain-community` (web search),
  `claude-agent-sdk` (delegation/reasoning). Browser + vision libs added in later phases.
- Secrets in `.env`: `ELEVENLABS_API_KEY`, `AGENT_ID`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` (optional).

## File map
- `main.py` — wires up the ElevenLabs `Conversation`, audio, and callbacks. **No business logic here.**
- `tools.py` — all client tools, registered on one `ClientTools` registry. One tool = one function.
- `memory/` — persistent memory store (added in the memory phase).
- `agents/` — delegated agent loops (added in the delegation phase).
- `generated/` — the ONLY folder tools may write user files into.
- `docs/` — project documentation and the progress log.

## Architecture rules
- Every tool is a function taking one `parameters` dict; read values with `parameters.get(...)`.
- Each tool returns a short string the voice agent will read aloud — keep returns concise.
- After adding a tool in code, REMIND ME to also register it in the ElevenLabs dashboard
  (name + description + parameters). The agent cannot call a tool it doesn't know about.
- Keep functions small, single-responsibility, easy to test.

## Safety rules (NON-NEGOTIABLE — do not weaken these)
- File writes go ONLY inside `./generated/`. Reject any path containing `..` or that is absolute.
- App / window / system actions run ONLY against an explicit allow-list. Unknown target → refuse politely.
- NO open-ended "run any shell command" tool. Voice + arbitrary shell = remote code execution risk.
- Any irreversible or sensitive action (delete, send message/email, purchase, submit form) must
  RETURN A CONFIRMATION REQUEST string, never execute directly.
- `delegate_task` runs with a hard `max_turns` limit and a timeout, and only allow-listed tools.
- Never read, print, log, or transmit `.env` values, secrets, passwords, or API keys.

## Error-awareness & verification (mutual checking)
Two LLMs (you and the planning chat) collaborating can compound mistakes — a plausible-but-wrong assumption from one gets executed confidently by the other. Stay actively skeptical:
- Assume you can be confidently wrong. When SDK/API/library behavior is uncertain, fetch the official docs instead of guessing; if still unsure, say so and ask Rafael — never invent.
- Before implementing a prompt from the planning chat, sanity-check it against the current code, the architecture, and the safety rules. If it looks wrong, mismatched, or unsafe, flag it and propose a correction BEFORE building — don't execute a bad instruction just because it was pasted.
- After any change, verify it actually works (run/check it) before marking it done. Never report success you haven't confirmed.
- Watch the recurring failure modes: a tool in code but not registered in the ElevenLabs dashboard; writes outside ./generated/; a missing allow-list; a "Next action" that doesn't match what really happened; silent assumptions about Rafael's environment or keys.
- When something breaks, diagnose from the real error/traceback, propose the smallest fix, and wait for Rafael's approval.

## Working style
- Use **plan mode** for any non-trivial change: propose a plan, wait for my approval, then build.
- Build and test ONE tool/feature at a time. Don't batch many tools into one change.
- When SDK behavior is uncertain, FETCH THE OFFICIAL DOCS instead of guessing:
  - ElevenLabs Python SDK: https://elevenlabs.io/docs/eleven-agents/libraries/python
  - Claude Agent SDK: https://platform.claude.com/docs/en/agent-sdk/overview
- `git commit` after every working tool/feature, with a clear message.

## ⭐ MANDATORY session ritual (this is what keeps us in sync)

> **`docs/PROGRESS.md` is the BRIDGE** between you (Claude Code) and a SEPARATE planning chat
> Rafael runs on Claude.ai. He cannot connect us directly — he manually carries `PROGRESS.md`
> between us. It is the **single source of truth** for this project. **If anything ever conflicts
> with `PROGRESS.md`, the file wins.** Keeping it accurate, clear, and genuinely useful for a
> zero-context reader is one of your most important jobs.

At the START of every session:
1. Read this file, then `docs/PROGRESS.md`. State the current phase and the single Next action
   before doing anything else.

At the END of every session (REQUIRED — not optional; if `PROGRESS.md` doesn't faithfully reflect
what just happened, treat it as a failure):
2. Update `docs/PROGRESS.md`:
   - Move finished items to "Done", note today's date.
   - Write the single clear "Next action" — self-contained, so a fresh reader can act on it.
   - Log decisions made and why (Decision log, newest first).
   - Note anything broken or half-finished under "Known issues / WIP".
   - Update the Tools table including **ElevenLabs dashboard** registration status — a tool
     that's in code but not in the dashboard is invisible to the agent; that gap must be visible.
   - If you notice a recurring gap, **improve the file's structure** too. You have full latitude.
3. Commit everything with a clear message.

## How to run
- Activate venv → ensure `.env` is filled → `python main.py` → talk to the agent → Ctrl+C to stop.
