# Project: JARVIS — personal voice assistant

> This file is your foundational memory. You (Claude Code) read it at the start of every
> session. Keep it lean (~150 lines). Detailed material lives in `docs/`. **At the start of
> every session, also read `docs/PROGRESS.md` to see where we are.**

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

## Working style
- Use **plan mode** for any non-trivial change: propose a plan, wait for my approval, then build.
- Build and test ONE tool/feature at a time. Don't batch many tools into one change.
- When SDK behavior is uncertain, FETCH THE OFFICIAL DOCS instead of guessing:
  - ElevenLabs Python SDK: https://elevenlabs.io/docs/eleven-agents/libraries/python
  - Claude Agent SDK: https://platform.claude.com/docs/en/agent-sdk/overview
- `git commit` after every working tool/feature, with a clear message.

## ⭐ MANDATORY session ritual (this is what keeps us in sync)
At the START of every session:
1. Read this file, then `docs/PROGRESS.md`. State what phase we're in and the next action.

At the END of every session (REQUIRED — not optional):
2. Update `docs/PROGRESS.md`:
   - Move finished items to "Done", note the date.
   - Write the single clear "Next action" so the next session starts instantly.
   - Log any decisions made and why (the "Decision log" section).
   - Note anything that broke or is half-finished under "Known issues / WIP".
3. If we added a tool, confirm whether it's been registered in the ElevenLabs dashboard yet.
4. Commit everything.

## How to run
- Activate venv → ensure `.env` is filled → `python main.py` → talk to the agent → Ctrl+C to stop.
