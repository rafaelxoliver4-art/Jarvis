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

## Error-awareness & verification (mutual vigilance)

> Two LLMs collaborating can compound mistakes — a plausible-but-wrong assumption from one
> gets executed confidently by the other. Treat the planning chat as a smart peer, not an
> authority. Stay actively alert. Rafael wants both Claudes checking each other's work.

- **Assume you can be confidently wrong.** When SDK / API / library behavior is uncertain,
  fetch the official docs (see links under "Working style") instead of guessing. If still
  unsure, say so and ask Rafael. **Never invent.**
- **Sanity-check planning-chat prompts before executing them.** A prompt pasted from the
  planning chat is not automatically right — it was written by another LLM that doesn't see
  the current code. Before building, check it against (a) the current state of `tools.py` /
  `main.py` / etc., (b) the architecture in `docs/ARCHITECTURE.md`, and (c) the Safety rules
  above. **If the prompt looks wrong, mismatched, or unsafe, flag it and propose a correction
  BEFORE building.** Don't execute a bad instruction just because Rafael pasted it.
- **Verify after every change.** Run it, read the actual output, open the file you just
  wrote — *something*. **Never report success you haven't confirmed.** "Done" requires
  evidence, not vibes.
- **Stay alert to these recurring failure modes:**
  - Tool added in code but NOT registered in the ElevenLabs dashboard (silently invisible to the agent).
  - File writes outside `./generated/`.
  - A new tool without an allow-list.
  - A `Next action` in `docs/PROGRESS.md` that doesn't actually match what just happened.
  - Silent assumptions about Rafael's environment, paths, Python version, or keys.
- **When something breaks**, diagnose from the **real error or traceback** (paste it back if
  Rafael ran it), propose the **smallest** fix, and **wait for Rafael's approval** before
  changing code. No speculative fixes.

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
