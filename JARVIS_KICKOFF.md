# JARVIS — Project Kickoff & Master Brief

> **This is the single source of truth for the JARVIS project.** It contains the goal, the
> architecture, the safety rules, the full build plan, every prompt, and the complete contents of
> every project file. You can hand this one file to Claude Code and it can build the entire
> foundation from it — no other files required.

---

## ⚡ How to use this file (do this first)

1. Save this file (`JARVIS_KICKOFF.md`) somewhere easy — e.g. onto your **Área de Trabalho (Desktop)**.
2. Open a terminal in that location and start **Claude Code** (`claude`).
3. Paste **THE KICKOFF PROMPT** below. That's it — Claude Code will read this whole file, create a
   dedicated `Jarvis` folder on your Desktop, write every project file into it, set up git and the
   virtual environment, and then stop and tell you the single next step.
4. You then create your real `.env` (paste your own API keys — never let the assistant handle keys),
   register the agent in the ElevenLabs dashboard, and start Phase 1.

---

## 🎯 THE KICKOFF PROMPT  (paste this into Claude Code)

```
You are helping me bootstrap a personal project called JARVIS — a voice-controlled agentic
assistant. This file (JARVIS_KICKOFF.md) is the complete project brief. Read it fully before
doing anything.

Then perform SETUP, in this exact order, and STOP for my approval before installing packages or
running the app:

1. Find my Desktop folder robustly. Check, in order: ~/Desktop, then ~/"Área de Trabalho"
   (my system is in Brazilian Portuguese), then the OS's known Desktop location. Tell me the
   full path you found and confirm it's correct before creating anything.

2. Inside the Desktop, create a dedicated project folder named "Jarvis". Everything for this
   project lives here and nowhere else. If it already exists, ask me before touching it.

3. Inside Jarvis/, create the full project structure and write every file using the EXACT
   contents from the "APPENDIX — PROJECT FILES" section at the end of this brief. Target layout:
       Jarvis/
       ├── README.md
       ├── CLAUDE.md
       ├── requirements.txt
       ├── .env.example
       ├── .gitignore
       ├── main.py            (from the appendix's main.py)
       ├── tools.py           (from the appendix's tools.py)
       ├── generated/.gitkeep
       └── docs/
           ├── ARCHITECTURE.md
           ├── BUILD_GUIDE.md
           ├── PROMPT_LIBRARY.md
           ├── PROGRESS.md
           └── CAPABILITIES.md

4. Create a Python virtual environment at Jarvis/venv. Do NOT install packages yet — just create
   the venv and tell me the activate command for my OS.

5. Copy .env.example to .env (leave all values as placeholders — I will fill in my real keys).

6. Initialize a git repo in Jarvis/ and make the first commit ("chore: scaffold Jarvis project").

7. STOP. Read docs/PROGRESS.md and tell me: the current phase, the single next action, and what I
   personally need to do (keys + ElevenLabs dashboard) before we can run Phase 1.

After setup, follow the rules in CLAUDE.md for all future work: use plan mode for non-trivial
changes, build one tool at a time, respect the safety rules, and ALWAYS do the session wrap-up
(update docs/PROGRESS.md + commit) at the end of every session.
```

> Alternative: if you'd rather not let it write all the files, you can instead drop the
> `jarvis-project.zip` (from our chat) onto your Desktop and tell Claude Code: *"Unzip
> jarvis-project.zip into a new folder called Jarvis on my Desktop, move main.py and tools.py
> from the starter/ subfolder up to the project root, then do steps 4–7 of the kickoff prompt."*

---

## 1. Project description & goal

JARVIS is a **voice-controlled, agentic personal assistant** that runs on your own computer. You
speak to it; it understands; it **does things** — opens applications, controls the browser,
creates and saves files, answers from the web, remembers your preferences, and takes on
multi-step tasks autonomously and reports back.

It is *not* a chatbot that describes how to do something. It's an agent with hands. We're building
it as our own code (rather than a no-code tool) so we fully control and understand it, and so we
can extend it without limits.

**Our north star:** be able to say *"Jarvis, research X, build me a page about it, open it, and
remember that I prefer Y"* — and have it actually do all of that, and remember.

**Why this beats the typical tutorial build:** we add (a) a **Claude reasoning brain**, (b)
**autonomous task delegation** via the Claude Agent SDK, (c) **persistent cross-session memory**,
and (d) **structural safety** so it's powerful without being dangerous.

## 2. Architecture (the mental model)

Three layers:

1. **Ears + Mouth — ElevenLabs Agents (cloud):** speech-to-text, text-to-speech (the Jarvis
   voice), and human-like turn-taking. The hard speech machinery, hosted for us.
2. **Brain — the agent's LLM (set to a Claude model in the ElevenLabs dashboard):** understands
   intent and decides *which tool to call*. Claude is chosen because reliable tool-calling is the
   entire point of an agent that acts.
3. **Hands — local Python "client tools" (our code):** functions on your machine that actually do
   things. "Making Jarvis do more" = adding more small, safe tools here.

Flow: *you speak → ElevenLabs transcribes → Claude reasons & picks a tool → our Python runs it →
the result flows back → Jarvis speaks it.*

For complex multi-step jobs, one special tool — `delegate_task(goal)` — hands the goal to an
autonomous **Claude Agent SDK** loop (the same engine as Claude Code, as a library). It plans,
executes many steps, self-corrects, and returns a summary Jarvis reads aloud. (Full detail in
`docs/ARCHITECTURE.md`.)

**Verified technical facts (current):**
- ElevenLabs Python SDK install: `pip install "elevenlabs[pyaudio]"`.
- Imports: `from elevenlabs.client import ElevenLabs`;
  `from elevenlabs.conversational_ai.conversation import Conversation, ClientTools`;
  `from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface`.
- Claude Agent SDK: `pip install claude-agent-sdk`;
  `from claude_agent_sdk import query, ClaudeAgentOptions`.
- If any SDK detail looks off, fetch the official docs (links in CLAUDE.md) rather than guessing.

## 3. The dedicated workspace (your Desktop)

Everything lives in **one folder named `Jarvis` on your Desktop (Área de Trabalho)**. Nothing
about this project should be scattered elsewhere. This keeps the project portable, easy to back
up, and easy for Claude Code to reason about. The kickoff prompt above creates it.

## 4. Safety rules (non-negotiable — also in CLAUDE.md)

- File writes go ONLY into `./generated/`. Reject any path with `..` or that is absolute.
- App / window / system actions run ONLY against an explicit allow-list. Unknown target → refuse.
- NO open-ended "run any shell command" tool — a microphone + arbitrary shell is a remote-code
  -execution risk.
- Any irreversible/sensitive action (delete, send, buy, submit a form) RETURNS A CONFIRMATION
  request; it never executes directly.
- `delegate_task` runs with a hard turn limit + timeout + allow-listed tools only.
- Never read, print, log, or transmit `.env` values, secrets, or API keys.
- Email/messaging tools (later): **draft only**, never auto-send.

## 5. The build plan (phases)

Each phase = one Claude Code prompt → test → commit. Full prompts are in `docs/BUILD_GUIDE.md`.

- **Phase 0 — Scaffold** (the kickoff prompt does this).
- **Phase 1 — Voice loop** working (no tools). Paste the Jarvis system prompt into the dashboard.
- **Phase 2 — First tool:** `open_application` (learn the write→register-in-code→register-in-
  dashboard→test pattern).
- **Phase 3 — Core tools:** `search_web`, `save_file`, `create_html_file`, `get_system_info`,
  `control_window`.
- **Phase 4 — Browser control:** `browse(task)` (Playwright/MCP, not pixel-clicking).
- **Phase 5 — Reasoning/delegation:** `delegate_task` via the Claude Agent SDK. The big "wow".
- **Phase 6 — Persistent memory:** `remember` / `recall`, loaded at session start.
- **Phase 7 — Polish:** wake word, screen vision, startup launch, tool log, tool router.

A satisfying first milestone = Phase 1–3 + `delegate_task` + memory. See `docs/CAPABILITIES.md`
for the full menu of where this can go (multi-agent orchestration, scheduled briefings, MCP
integrations, etc.).

## 6. The working loop (how this chat + Claude Code stay in sync) ⭐

- **This Claude chat = the architect:** research, design, planning, writing prompts, getting
  unstuck. Come here to decide *what* to build next.
- **Claude Code = the builder:** writes, runs, debugs, commits the code in the `Jarvis` folder.
- **The docs in the folder = the shared brain.** Both read them; both keep them current.
- **`docs/PROGRESS.md` = the baton.** Claude Code reads it at the start of every session and is
  REQUIRED to update it at the end (current phase, the single next action, decisions, issues).
  Whenever you wonder "where were we?", that one file answers it.

**Each session:** plan here → get a precise prompt → build in Claude Code (plan mode) → test →
Claude Code updates `PROGRESS.md` + commits → next time, bring the new "Next action" back here.

## 7. What you (the human) must do — quick checklist

- [ ] Run the kickoff prompt in Claude Code to create the `Jarvis` folder on your Desktop.
- [ ] Install Python 3.11+, Node.js, and Claude Code if you haven't.
- [ ] In **ElevenLabs**: create an Agent → copy its **Agent ID** → create an **API key** → set the
      agent's LLM to a **Claude** model → paste the Jarvis system prompt (in `docs/PROMPT_LIBRARY.md`).
- [ ] Get an **Anthropic API key** (for Phase 5). OpenAI key only if you want images.
- [ ] Fill your real keys into `Jarvis/.env`.
- [ ] Approve Claude Code's package install, then run Phase 1.

---

# APPENDIX — PROJECT FILES

Below are the **exact, verified contents** of every file in the project. Claude Code: create each
file at the path given in its header, with the content exactly as shown. (Each file is wrapped in
`~~~` fences so that any backtick code blocks inside it are preserved verbatim.)

### FILE: `README.md`
~~~
# JARVIS — Personal Voice Assistant

> A voice-controlled, agentic personal assistant that listens, reasons, and *acts* on your
> computer — opening apps, controlling the browser, managing files, and handling multi-step
> tasks on its own. Built incrementally by a human + Claude (this chat) + Claude Code, working
> together as one team.

This repository is **self-documenting**. Every file here exists so that you, this Claude chat,
and Claude Code can always pick up exactly where the project left off — even months later.

---

## Read these in order

1. **`README.md`** (this file) — the vision and the menu of what's possible.
2. **`CLAUDE.md`** — the rules of the project. Claude Code reads this automatically every session.
3. **`docs/ARCHITECTURE.md`** — how the system is designed and why.
4. **`docs/BUILD_GUIDE.md`** — the step-by-step build, with the exact prompts to paste into Claude Code.
5. **`docs/PROMPT_LIBRARY.md`** — reusable prompts for both this chat and Claude Code.
6. **`docs/PROGRESS.md`** — the living log. The "baton" passed between sessions. **Always update it.**
7. **`docs/CAPABILITIES.md`** — the full capability roadmap, tiered from simple to ambitious.

---

## The vision

A real-life JARVIS. You speak; it understands; it does the thing. Not a chatbot that *describes*
how to do something — an agent that opens your apps, runs your tasks, browses the web for you,
remembers your preferences, and takes on complex jobs while you do something else.

We're building this the way the best 2026 assistants are built, but as **our own code** so we
fully control and understand it.

## What it can do (today's plan → tomorrow's ambition)

**Core (we build this first):**
- Natural voice conversation with a witty "Jarvis" personality.
- Open and control desktop applications by voice.
- Search the web and save results to files.
- Create documents and web pages on command.
- Report system info (time, battery, etc.).

**Agentic (the part that feels like the movies):**
- **Reasoning & delegation** — hand complex, multi-step goals to an autonomous Claude agent
  loop that plans and executes on its own, then reports back by voice.
- **Persistent memory** — remembers facts, preferences, and past tasks across sessions.
- **Browser control** — navigates real websites and pulls/acts on information.
- **Screen awareness** — "what's on my screen right now?" via screenshot + OCR.

**Ambitious (where this could go):**
- Multi-agent orchestration: one main Jarvis directing specialized sub-agents (research, email, calendar).
- Proactive/scheduled tasks: briefings, reminders, background work while you sleep.
- Unlimited integrations via MCP servers (calendar, email, music, smart home).

See `docs/CAPABILITIES.md` for the full menu and the order we'll tackle it.

## The three-layer architecture (the key mental model)

```
   YOU  ──speak──▶  ElevenLabs Agent  ──decides──▶  Local Python Tools  ──act──▶  YOUR COMPUTER
                    (ears + mouth +                 (the "hands":               (apps, files,
                     Claude brain)                   open app, browse,           browser, web)
                                                     delegate_task...)
        ◀──speaks back──  (narrates the result in Jarvis's voice)
```

- **ElevenLabs Agents** = speech-in, speech-out, turn-taking, and the conversational LLM.
  We set that LLM to a **Claude model** (best at deciding *when* and *how* to use tools).
- **Local Python tools** = functions on *your* machine that the agent calls to actually do things.
- For hard, multi-step jobs, one special tool (`delegate_task`) spins up the **Claude Agent SDK**
  — an autonomous agent loop — to plan and execute, then return a summary Jarvis reads aloud.

Full detail in `docs/ARCHITECTURE.md`.

## How the humans and the two Claudes work together

- **This chat (Claude.ai)** is the **architect**: research, design, planning, generating prompts,
  getting unstuck, reviewing decisions.
- **Claude Code** is the **builder**: writes/edits code, runs it, debugs, commits.
- **The docs in this repo** are the **shared brain**. Both read them; both keep them current.
- **`docs/PROGRESS.md`** is the **handoff baton** — the last thing updated each session and the
  first thing read the next. This is what makes the collaboration *continuous*.

See `docs/BUILD_GUIDE.md` → "The working loop" for the exact ritual.

## Status

Project just started. See `docs/PROGRESS.md` for current phase and next action.

## A note on safety

This assistant can run programs and control your computer by voice. That power needs guardrails
(allow-lists, a file sandbox, confirmation before irreversible actions, no open-ended shell).
These rules live in `CLAUDE.md` and are non-negotiable. Read them before building.
~~~

### FILE: `CLAUDE.md`
~~~
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
~~~

### FILE: `requirements.txt`
~~~
# Core voice loop
elevenlabs[pyaudio]
python-dotenv

# Tools
psutil                 # system info
langchain-community    # free DuckDuckGo web search

# Reasoning / delegation (Phase 5)
claude-agent-sdk

# Added in later phases as needed:
# playwright           # browser control (Phase 4)
# pillow               # screen vision / image handling (Phase 7)
# openai               # image generation (optional)
# chromadb             # semantic memory upgrade (optional)
~~~

### FILE: `.env.example`
~~~
# Copy this file to ".env" and fill in your real values. NEVER commit .env.

# --- ElevenLabs (required) ---
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
AGENT_ID=your_elevenlabs_agent_id_here

# --- Anthropic (required for the delegate_task / reasoning phase) ---
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# --- OpenAI (optional — only if you add image generation) ---
# OPENAI_API_KEY=your_openai_api_key_here
~~~

### FILE: `.gitignore`
~~~
# Secrets — never commit
.env

# Python
venv/
__pycache__/
*.pyc
.pytest_cache/

# Assistant output and local memory
generated/
memory/*.local
memory/*.db

# OS / editor
.DS_Store
.vscode/
.idea/
~~~

### FILE: `main.py`
~~~
"""
JARVIS — main voice loop (STARTER SKELETON)

This file only WIRES UP the conversation: audio, callbacks, and the client-tool registry.
All actual capabilities live in tools.py. Keep business logic OUT of this file.

Run:  python main.py   (after activating the venv and filling in .env)
Stop: Ctrl+C

If the SDK API has changed, fetch the current docs:
  https://elevenlabs.io/docs/eleven-agents/libraries/python
"""

import os
import signal

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

# Our local capabilities (the "hands"). Defined and registered in tools.py.
from tools import client_tools

load_dotenv()

AGENT_ID = os.getenv("AGENT_ID")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")


def main() -> None:
    if not AGENT_ID:
        raise SystemExit("Missing AGENT_ID in .env (copy it from your ElevenLabs agent).")

    elevenlabs = ElevenLabs(api_key=ELEVENLABS_API_KEY)

    conversation = Conversation(
        elevenlabs,
        AGENT_ID,
        # Auth is needed only for private agents (i.e. when an API key is set).
        requires_auth=bool(ELEVENLABS_API_KEY),
        audio_interface=DefaultAudioInterface(),
        # Our local tools the agent can call:
        client_tools=client_tools,
        # Console callbacks so we can see what's happening:
        callback_agent_response=lambda r: print(f"JARVIS: {r}"),
        callback_agent_response_correction=lambda o, c: print(f"JARVIS (corrected): {o} -> {c}"),
        callback_user_transcript=lambda t: print(f"You: {t}"),
    )

    # Clean shutdown on Ctrl+C.
    signal.signal(signal.SIGINT, lambda sig, frame: conversation.end_session())

    print("JARVIS is listening. Speak now. Press Ctrl+C to stop.\n")
    conversation.start_session()

    conversation_id = conversation.wait_for_session_end()
    print(f"\nConversation ended. ID: {conversation_id}")


if __name__ == "__main__":
    main()
~~~

### FILE: `tools.py`
~~~
"""
JARVIS — client tools (STARTER SKELETON: the "hands")

Each tool is a function that takes ONE `parameters` dict and returns a SHORT string the voice
agent will read aloud. Every tool here follows the safety rules in CLAUDE.md:
  - file writes go ONLY into ./generated/  (no "..", no absolute paths)
  - app/system actions use an ALLOW-LIST (unknown target -> polite refusal)
  - no open-ended shell; irreversible actions must ask for confirmation

REMEMBER: registering a tool in code is only half the job. You must ALSO register it in the
ElevenLabs dashboard (matching name + description + parameters) or the agent can't call it.
"""

import os
import platform
import subprocess

from elevenlabs.conversational_ai.conversation import ClientTools

# ---------------------------------------------------------------------------
# Safety helpers
# ---------------------------------------------------------------------------

GENERATED_DIR = os.path.join(os.path.dirname(__file__), "generated")
os.makedirs(GENERATED_DIR, exist_ok=True)


def _safe_path(file_name: str) -> str:
    """Resolve a filename to a path INSIDE ./generated/, refusing escapes."""
    if not file_name or os.path.isabs(file_name) or ".." in file_name.replace("\\", "/").split("/"):
        raise ValueError("unsafe file name")
    path = os.path.realpath(os.path.join(GENERATED_DIR, file_name))
    if not path.startswith(os.path.realpath(GENERATED_DIR) + os.sep):
        raise ValueError("path escapes the generated/ sandbox")
    return path


# Friendly name -> how to launch it, per OS. Extend this list deliberately.
APP_ALLOW_LIST = {
    "chrome":     {"Windows": "chrome",      "Darwin": "Google Chrome", "Linux": "google-chrome"},
    "vscode":     {"Windows": "code",        "Darwin": "Visual Studio Code", "Linux": "code"},
    "calculator": {"Windows": "calc",        "Darwin": "Calculator",    "Linux": "gnome-calculator"},
    "notes":      {"Windows": "notepad",     "Darwin": "Notes",         "Linux": "gedit"},
    "spotify":    {"Windows": "spotify",     "Darwin": "Spotify",       "Linux": "spotify"},
}


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

def open_application(parameters) -> str:
    """Open an allow-listed desktop application by friendly name."""
    app = (parameters.get("app_name") or "").strip().lower()
    entry = APP_ALLOW_LIST.get(app)
    if not entry:
        allowed = ", ".join(sorted(APP_ALLOW_LIST))
        return f"I'm not permitted to open '{app}', sir. I can open: {allowed}."

    system = platform.system()
    target = entry.get(system)
    if not target:
        return f"I don't have a way to open {app} on this system, sir."

    try:
        if system == "Darwin":
            subprocess.Popen(["open", "-a", target])
        elif system == "Windows":
            subprocess.Popen(target, shell=True)
        else:  # Linux
            subprocess.Popen([target])
        return f"Opening {app}, sir."
    except Exception as exc:  # noqa: BLE001 - surface a friendly message
        return f"I couldn't open {app}: {exc}."


def save_file(parameters) -> str:
    """Save text to a file inside ./generated/ only."""
    file_name = parameters.get("file_name") or "note.txt"
    data = parameters.get("data") or ""
    try:
        path = _safe_path(file_name)
    except ValueError:
        return "That file location isn't allowed, sir. I can only save inside the generated folder."
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(data)
    return f"Saved to {os.path.basename(path)}, sir."


def delegate_task(parameters) -> str:
    """
    Hand a complex, multi-step goal to an autonomous Claude Agent SDK loop.

    STUB: implemented fully in the delegation phase (see docs/BUILD_GUIDE.md Phase 5).
    When built, it must use ClaudeAgentOptions with an allowed_tools allow-list, a hard
    max_turns cap, a timeout, and permission_mode that confirms destructive actions.
    """
    goal = parameters.get("goal") or ""
    if not goal:
        return "What would you like me to take on, sir?"
    return ("I can't run autonomous tasks yet, sir — the delegation engine isn't built. "
            "Add it per Phase 5 of the build guide.")


# ---------------------------------------------------------------------------
# Registry  (the agent calls tools by these registered names)
# ---------------------------------------------------------------------------

client_tools = ClientTools()
client_tools.register("open_application", open_application)
client_tools.register("save_file", save_file)
client_tools.register("delegate_task", delegate_task)

# Dashboard registration cheat-sheet (add these as Client Tools in ElevenLabs):
#   open_application — "Open a desktop app the user names."   param: app_name (string)
#   save_file        — "Save text to a file."                 params: file_name (string), data (string)
#   delegate_task    — "Run a complex multi-step task."       param: goal (string)
~~~

### FILE: `docs/ARCHITECTURE.md`
~~~
# Architecture

This document explains *how* JARVIS is built and *why*. Read it before any structural change.

---

## The three layers

```
   YOU
    │  speak
    ▼
┌─────────────────────────────────────────────┐
│ LAYER 1 — EARS + MOUTH (ElevenLabs Agents)   │   Cloud-hosted.
│  • Speech-to-text                            │   Hard to build well ourselves,
│  • Text-to-speech (the Jarvis voice)         │   so we let ElevenLabs host it.
│  • Human-like turn-taking / interruptions    │
└───────────────────┬─────────────────────────┘
                    │ holds an open connection to our script
                    ▼
┌─────────────────────────────────────────────┐
│ LAYER 2 — BRAIN (the agent's LLM = Claude)   │   Set in the ElevenLabs dashboard.
│  • Understands intent                        │   Claude is chosen because it is the
│  • Decides WHICH tool to call and with what  │   most reliable at tool-calling, which
│  • Holds the conversation                    │   is the entire point of an acting agent.
└───────────────────┬─────────────────────────┘
                    │ calls a "client tool"
                    ▼
┌─────────────────────────────────────────────┐
│ LAYER 3 — HANDS (our local Python tools)     │   Runs on YOUR machine (tools.py).
│  • open_application, search_web, save_file…  │   This is where we add capability.
│  • browse (browser control)                  │   "Doing more" = adding more tools here.
│  • delegate_task → autonomous Claude loop     │
└───────────────────┬─────────────────────────┘
                    │ acts
                    ▼
            YOUR COMPUTER (apps, files, browser, web)
                    │
                    └── result ──▶ back up to Layer 2 ──▶ Jarvis speaks it (Layer 1)
```

**The one-sentence model:** *You speak → ElevenLabs transcribes → Claude reasons and picks a
tool → our local Python runs it → the result flows back and Jarvis narrates it.*

**The key consequence:** almost everything you want ("open this", "do that", "research and
build") is just **adding another tool to Layer 3** plus a good system prompt in Layer 2. There
is no need to rebuild the hard speech machinery.

---

## How a "client tool" works (the core mechanism)

The ElevenLabs Python SDK keeps a live connection open while a conversation runs. We register
Python functions as **client tools**. When Claude (Layer 2) decides to call one, ElevenLabs
sends the call down the connection, our function executes locally, and we return a short string
that Claude then speaks.

Two registrations are required for every tool:
1. **In code** — register the function on the `ClientTools` registry (in `tools.py`).
2. **In the ElevenLabs dashboard** — add a Client Tool with a matching name, a clear
   description (so the LLM knows *when* to use it), and the parameter definitions.

If either registration is missing, the tool silently won't work. This is the #1 gotcha.

Confirmed current SDK imports:
```python
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface
from elevenlabs.conversational_ai.conversation import ClientTools
```

---

## Two levels of reasoning

**Level 1 — direct tool calls (build first).** Claude in Layer 2 calls one tool at a time:
"open Chrome", "search the web", "save a file". Reliable and enough for most commands.

**Level 2 — delegated autonomy (the "wow").** For goals that need many steps, we expose ONE
tool, `delegate_task(goal)`. It hands the goal to a **Claude Agent SDK** loop running locally —
the same engine that powers Claude Code, as a library. That loop plans, calls its own tools
(file I/O, web, browser), self-corrects over multiple turns, and returns a concise summary that
Jarvis reads aloud.

```python
# Sketch of the delegation tool (full version built in the delegation phase)
from claude_agent_sdk import query, ClaudeAgentOptions

async def _run_delegated(goal: str) -> str:
    result_chunks = []
    async for message in query(
        prompt=goal,
        options=ClaudeAgentOptions(
            system_prompt="You are Jarvis's task executor. Accomplish the goal, then summarize.",
            allowed_tools=["Read", "Write", "WebSearch"],   # allow-list only
            permission_mode="default",                       # asks before destructive actions
            max_turns=12,                                    # hard cap
        ),
    ):
        result_chunks.append(message)
    return summarize(result_chunks)
```

Why this is powerful: complex requests ("research the 3 best keyboards under $150, make a
comparison page, and open it") become a single spoken sentence. The voice agent stays snappy;
the heavy thinking happens in the delegated loop.

---

## Memory (added after core is stable)

Three kinds, mirrored from how the best 2026 assistants are built:
- **Working memory** — the current conversation. ElevenLabs handles this within a session.
- **Persistent memory** — facts and preferences that survive across sessions ("I use VS Code",
  "my projects live in ~/dev"). Stored locally in `memory/` (a JSON store to start; a small
  vector store like Chroma later for semantic recall). Exposed via `remember(fact)` and
  `recall(query)` tools, and injected into the agent's context at session start.
- **Procedural memory** — learned how-tos ("the way I like my morning briefing"). Saved as small
  reusable recipes the assistant can replay.

Privacy-first: memory stays on your machine. Nothing about you is sent anywhere it doesn't need
to go.

---

## Planner & tool router (add when tools get numerous)

- **Task planner:** before executing a multi-step request, decompose it into an ordered list of
  sub-steps. This dramatically improves multi-step reliability. (For us, `delegate_task` gets
  this "for free" from the Agent SDK loop; a standalone planner is optional.)
- **Tool router:** once we have many tools, showing all of them to the LLM every turn causes
  "context rot" and wrong-tool picks. A router surfaces only the relevant subset per request
  (keyword or embedding based). Not needed early; plan for it past ~15–20 tools.

---

## Folder layout (target)

```
jarvis/
├── main.py            # voice loop wiring only
├── tools.py           # all client tools on one registry
├── memory/            # persistent + procedural memory store
├── agents/            # delegated Claude Agent SDK loops
├── generated/         # the ONLY writable output folder
├── .env               # secrets (never committed)
├── CLAUDE.md          # Claude Code's foundational memory
└── docs/              # this folder
```

---

## Design principles

1. **Capability = tools.** Want it to do more? Add a small, safe tool. Don't bloat the core.
2. **The LLM decides; the tools do.** Keep tools dumb, deterministic, and well-described.
3. **Safety is structural, not just prompted.** Allow-lists and sandboxes live in the code, so a
   misheard command can't cause damage even if the prompt is ignored.
4. **Local-first & private.** Your data and memory stay on your machine by default.
5. **Documented continuity.** Every session updates `PROGRESS.md` so we never lose the thread.
~~~

### FILE: `docs/BUILD_GUIDE.md`
~~~
# Build Guide — step by step, with the exact prompts

This is the playbook. Work top to bottom. Each phase = a prompt to paste into **Claude Code**,
then a **test**, then a **commit**. Don't skip the ritual at the bottom — it's what keeps this
project alive across sessions.

---

## Before you start (do these yourself — never let an assistant handle keys/accounts)

- [ ] Install **Python 3.11+** and **Node.js**.
- [ ] Install **Claude Code** (`npm install -g @anthropic-ai/claude-code`; verify current command at docs.claude.com).
- [ ] **ElevenLabs:** create an Agent → copy its **Agent ID** → create an **API key** → set the
      agent's LLM to a **Claude** model in the dashboard.
- [ ] **Anthropic API key** (for the delegation phase). **OpenAI key** only if you want images.
- [ ] Working mic + speakers. On macOS, be ready to grant Accessibility + Microphone permissions.
- [ ] Drop this whole `jarvis-project/` folder where you want the repo to live, then open it in
      Claude Code (`cd` into it and run `claude`).

---

## The working loop (how this chat + Claude Code collaborate) ⭐

Repeat this for every work session. It's the heart of "continuously work together."

1. **Plan here (Claude.ai chat).** Decide what to build next. Ask this chat to refine the goal,
   research anything new, and hand you a precise Claude Code prompt. (Use the `PROMPT_LIBRARY.md`.)
2. **Build there (Claude Code).** Open the repo. Claude Code reads `CLAUDE.md` + `docs/PROGRESS.md`,
   states the current phase, then executes the prompt in **plan mode** (review → approve → build).
3. **Test.** Run it. If it breaks, paste the FULL error back to Claude Code (or to this chat).
4. **Wrap up (REQUIRED).** Claude Code updates `docs/PROGRESS.md` (done / next action / decisions /
   issues), confirms dashboard registration, and commits.
5. **Carry the baton back.** Next time, paste the latest `PROGRESS.md` "Next action" into this chat
   to plan the following step. The log is the shared memory between sessions.

> If you ever feel lost, the answer is always: open `docs/PROGRESS.md`. It tells you exactly
> where you are and what's next.

---

## Phase 0 — Scaffold

**Claude Code prompt:**
```
Read CLAUDE.md and docs/PROGRESS.md first. Then scaffold this Python project: create a venv in
./venv, a .gitignore (ignore .env, venv/, __pycache__/, generated/, memory/*.local), a
requirements.txt, an empty tools.py, a main.py, a .env.example with ELEVENLABS_API_KEY, AGENT_ID,
ANTHROPIC_API_KEY, and a commented OPENAI_API_KEY, and a generated/ folder with a .gitkeep.
Initialize git and make the first commit. No logic yet — skeleton only. Show me the file tree,
then update docs/PROGRESS.md per the session ritual.
```
Then copy `.env.example` → `.env` yourself and paste in your real keys.

**Test:** file tree looks right, `.env` is git-ignored. **Commit.**

---

## Phase 1 — The voice loop (no tools yet)

**Claude Code prompt:**
```
Implement the ElevenLabs Agents voice loop in main.py using the official Python SDK (fetch
https://elevenlabs.io/docs/eleven-agents/libraries/python if you need to confirm the API). Load
ELEVENLABS_API_KEY and AGENT_ID from .env with python-dotenv. Create the ElevenLabs client, start
a Conversation with DefaultAudioInterface(), wire callbacks that print the agent response and my
transcript, handle Ctrl+C with a signal handler that calls end_session(), and print the
conversation ID at the end. Add elevenlabs[pyaudio] and python-dotenv to requirements and install
them. Tell me exactly how to run it, then do the session wrap-up.
```

**Test:** run it, say hello, Jarvis replies. PyAudio audio errors usually mean missing system
audio libs — paste the error to Claude Code. **Commit.**

Also paste the **Jarvis system prompt** (see `PROMPT_LIBRARY.md` → "Agent system prompt") into the
ElevenLabs dashboard now, and pick the "Charlie"-style voice.

---

## Phase 2 — First real tool: open_application (learn the pattern)

**Claude Code prompt:**
```
Add client-side tools. In tools.py create a ClientTools registry and a function
open_application(parameters) that reads parameters.get('app_name') and launches that app
cross-platform. Validate app_name against an ALLOW-LIST dict mapping friendly names to executables
(start with chrome, vscode, calculator, notes/notepad, spotify). If the app isn't allow-listed,
return a polite refusal string and run nothing. Register it as open_application. In main.py import
the registry and pass client_tools= into the Conversation. Put the exact registration name +
parameter names in a comment for me to copy into the ElevenLabs dashboard. Then do the wrap-up.
```

**Then in the ElevenLabs dashboard:** add a Client Tool `open_application`, description
"Open a desktop application the user names", parameter `app_name` (string). Save the agent.

**Test:** "Jarvis, open Chrome." **Commit.**

> 🎓 You now know the whole pattern: **write tool → register in code → register in dashboard →
> test by voice → commit.** Every capability below is this same loop.

---

## Phase 3 — Core capability set (one at a time)

Use the reusable template in `PROMPT_LIBRARY.md` → "Add a tool". Build, register, test, commit
each before the next:

- `search_web(query)` — DuckDuckGo via `langchain-community` (free, no key). Returns text.
- `save_file(file_name, data, folder)` — writes text into `./generated/` only; reject `..`/absolute paths.
- `create_html_file(file_name, title, data)` — styled HTML page into `./generated/`, optionally opens it.
- `get_system_info()` — time, date, battery, CPU/RAM via `psutil`. Read-only, safe.
- `control_window(action, app_name)` — focus/minimize/close, allow-listed actions only.

---

## Phase 4 — Browser control (big capability jump)

Prefer real browser automation (Playwright / an MCP browser server) over blind pixel-clicking,
which breaks the moment the screen changes.

**Claude Code prompt:**
```
Research current options for browser control from Python (Playwright-driven vs. an MCP browser
server) and recommend the more reliable one for a personal assistant. Then implement a
browse(task) client tool that drives a real browser to accomplish a described web task and returns
a short summary. Keep navigation to an allow-list of domains I provide. Any action that submits a
form, sends a message, or makes a purchase must return a confirmation request to me instead of
doing it automatically. Wrap up when done.
```

**Test:** "Jarvis, look up today's weather and tell me." **Commit.**

---

## Phase 5 — Reasoning & delegation (Level 2 — the "wow")

**Claude Code prompt:**
```
Add a delegate_task(goal) client tool backed by the Claude Agent SDK (pip install
claude-agent-sdk; fetch https://platform.claude.com/docs/en/agent-sdk/overview to confirm the
API). When called, run an autonomous agent loop with the goal: use ClaudeAgentOptions with a
focused system_prompt, an allowed_tools allow-list (Read, Write, WebSearch, plus our browse if
feasible), permission_mode="default", and a hard max_turns cap (~12) and an overall timeout.
Stream progress to the console and return a concise final summary string for Jarvis to speak. Put
the loop in agents/. Never allow unrestricted shell. Wrap up when done.
```

**Test (multi-step):** "Jarvis, research the three best mechanical keyboards under $150, save a
comparison as an HTML page, and open it." **Commit.**

---

## Phase 6 — Persistent memory

**Claude Code prompt:**
```
Add persistent memory. Create memory/ with a local JSON store and two tools: remember(fact) saves
a durable fact/preference, recall(query) returns relevant saved facts. At session start in
main.py, load a short summary of memory and include it in the conversation context so Jarvis
"knows" me. Keep everything local; never transmit memory anywhere. Later we may upgrade to a small
vector store for semantic recall — leave a clean seam for that. Wrap up when done.
```

**Test:** tell it a preference, restart, confirm it remembers. **Commit.**

---

## Phase 7 — Polish (pick what you want)

- **Wake word** — only start a session when it hears "Jarvis" (e.g. an offline wake-word detector).
- **Screen vision** — `look_at_screen()`: screenshot + OCR so it can answer "what's on my screen?".
- **Launch on startup** so Jarvis is always available.
- **Tool log** — record which tools were called, for debugging and trust.
- **Tool router** — once you pass ~15–20 tools, surface only relevant ones per request.

For each: plan in this chat → get a prompt → build in Claude Code → test → commit → update PROGRESS.

---

## Troubleshooting quick hits

- **Tool never fires:** it's almost always missing/incorrect **dashboard registration** (name or
  parameter mismatch with the code). Check both sides match exactly.
- **Audio/PyAudio errors:** missing system audio libraries; paste the error to Claude Code.
- **Agent talks too much:** tighten the system prompt ("one or two short sentences").
- **Wrong tool chosen:** improve the tool's *description* in the dashboard — that's what the LLM reads.
- **Delegated task runs forever:** lower `max_turns`, ensure the timeout fires.
- **Lost the thread:** open `docs/PROGRESS.md`.
~~~

### FILE: `docs/PROMPT_LIBRARY.md`
~~~
# Prompt Library

Copy-paste prompts for the two Claudes and the ElevenLabs agent. Reuse these constantly.

---

## A. The ElevenLabs agent system prompt (paste into the dashboard)

Put this in the agent's **System Prompt** field.

```
# Persona
You are JARVIS, a witty, hyper-competent digital butler — dry and lightly sarcastic, but always
genuinely helpful and never mean. You address the user as "sir".

# Goal
Help the user by understanding intent and accomplishing it with your tools. Prefer doing the task
over describing it.

# Tools & reasoning
- You have tools that control the user's computer (open apps, files, browser) and a delegate_task
  tool for complex multi-step jobs.
- Briefly decide which tool fits before calling it. If a request needs several steps, prefer
  delegate_task over chaining many small calls yourself.
- If you lack a tool for something, say so plainly rather than pretending.

# Rules
- Keep spoken answers to one or two short sentences. This is voice; be concise.
- Before any irreversible/sensitive action (delete, send, buy, submit a form), confirm first.
- If a tool errors, explain the failure in one sentence and suggest a fix.
- Never read long file contents, code, or URLs aloud — say you've saved/opened it instead.
- Stay in character, but accuracy and safety always beat the bit.
```

---

## B. Reusable Claude Code prompts

### Start of session (paste first, every time)
```
Read CLAUDE.md and docs/PROGRESS.md. Tell me the current phase and the single next action, then
wait for my go-ahead.
```

### Add a new tool (the workhorse template)
```
Add a new client tool <NAME>(parameters) to tools.py, following the EXACT same pattern, error
handling, and safety discipline (allow-list / generated-only sandbox) as open_application. It
should <what it does>, reading <which parameters>. Register it as <name>. Then give me the
ElevenLabs dashboard registration details (description + parameter list) to paste in. Plan first,
then implement after I approve. Wrap up per the session ritual when done.
```

### Debug
```
Here is the full error and what I did:
<paste full traceback + steps>
Diagnose the root cause, propose the smallest fix, and wait for approval before changing code.
```

### End of session (if Claude Code forgets the ritual)
```
Do the session wrap-up now: update docs/PROGRESS.md (move done items, write the single Next
action, log decisions, note WIP/issues), confirm which tools still need dashboard registration,
and commit everything.
```

### Refactor / safety review
```
Review tools.py against the safety rules in CLAUDE.md. Flag any tool that can write outside
./generated/, act without an allow-list, run open-ended shell, or perform an irreversible action
without confirmation. Propose fixes; don't apply them until I approve.
```

---

## C. Reusable prompts for THIS chat (the architect)

### Plan the next feature
```
Here's the current Next action from PROGRESS.md: <paste it>. Help me think it through — design,
risks, the cleanest approach — then write a precise Claude Code prompt I can paste to build it.
```

### Research a capability
```
Research the best current way to <capability, e.g. "give Jarvis access to my calendar"> for a
local, privacy-first personal assistant in 2026. Compare the main options, recommend one for our
architecture, and outline how it'd plug in as a tool or MCP server.
```

### Review a decision
```
We're deciding between <A> and <B> for <purpose>. Given our architecture (ElevenLabs + Claude
brain + local tools + Claude Agent SDK delegation), which fits better and why? Note the trade-offs.
```

### Generate the dashboard registration text
```
For this tool function <paste function>, write the ElevenLabs Client Tool registration: a clear
description (so the LLM knows when to use it) and the parameter definitions.
```

---

## D. Voice command ideas to test each phase

- Phase 1: "Hello Jarvis, how are you?"
- Phase 2: "Open VS Code."
- Phase 3: "Search the web for the best ramen in town and save it to a file." / "What's my battery at?"
- Phase 4: "Pull up today's weather and tell me if I need a jacket."
- Phase 5: "Research the 3 best budget mechanical keyboards, make a comparison page, and open it."
- Phase 6: "Remember that I prefer dark mode and my code lives in ~/dev." (then restart and ask)
- Phase 7: "What's on my screen right now?"
~~~

### FILE: `docs/PROGRESS.md`
~~~
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
~~~

### FILE: `docs/CAPABILITIES.md`
~~~
# Capabilities — the full menu (what this could become)

A tiered roadmap, informed by how the strongest 2026 personal assistants are actually built
(open-source projects like local-first JARVIS clones, agentic frameworks, and the Claude Agent
SDK). Each item is "just another tool" on Layer 3 — build them with the standard loop in
`BUILD_GUIDE.md`. Don't build everything; pick what *you* want.

Legend: 🟢 easy · 🟡 medium · 🔴 ambitious

---

## Tier 1 — Core (the foundation)
- 🟢 **Voice conversation** with the Jarvis personality.
- 🟢 **Open applications** by name (allow-listed).
- 🟢 **Web search** + **save to file**.
- 🟢 **Create documents / HTML pages**.
- 🟢 **System info** (time, battery, CPU/RAM).
- 🟡 **Window control** (focus / minimize / close, allow-listed).

## Tier 2 — Agentic (where it starts to feel like JARVIS)
- 🟡 **Delegated reasoning** (`delegate_task`) — autonomous multi-step jobs via the Claude Agent
  SDK. *The single highest-impact upgrade.*
- 🟡 **Browser control** — navigate real sites, pull info, fill forms (with confirmation on
  consequential actions). Prefer Playwright/MCP over pixel-clicking.
- 🟡 **Persistent memory** — remembers facts, preferences, and past tasks across sessions
  (local JSON → vector store for semantic recall).
- 🟡 **Screen vision** — screenshot + OCR so it can answer "what's on my screen?".
- 🟢 **Media control** — play/pause/skip music (Spotify), play YouTube.
- 🟢 **Image generation** — via OpenAI `gpt-image-1` (optional, needs OpenAI key).

## Tier 3 — Integrations (connect it to your life)
- 🟡 **Calendar** — read your schedule, draft events (you confirm). Via API or an MCP server.
- 🟡 **Email** — summarize/triage and **draft** replies (you hit send). Never auto-send.
- 🟡 **Notes / to-dos** — capture and retrieve tasks by voice.
- 🟡 **MCP servers** — the expansion port. ElevenAgents and the Agent SDK both support MCP, so you
  can plug in hundreds of community integrations (files, search, dev tools, smart home) without
  writing each from scratch. Watch the tool-count ceiling (~40–50 visible tools) — use a tool
  router past that.
- 🔴 **Smart home** — lights, thermostat, locks (if you have compatible hardware).

## Tier 4 — Autonomy & orchestration (the frontier)
- 🔴 **Multi-agent orchestration** — one main Jarvis directing specialized sub-agents (a research
  agent, an email agent, a calendar agent), each with its own tools and scope. The Agent SDK
  supports spawning subagents.
- 🔴 **Proactive / scheduled tasks** — execution modes beyond on-demand: a scheduled morning
  briefing (weather + calendar + headlines, spoken), reminders, or background jobs that run while
  you sleep and report when done.
- 🔴 **Task planner** — decompose complex requests into ordered sub-steps before executing, for
  higher multi-step reliability (largely covered by `delegate_task`'s loop).
- 🔴 **Procedural memory / skills** — teach it repeatable "recipes" ("do my usual standup prep")
  it can replay. The open `agentskills` standard is one way to package these.
- 🔴 **Self-improving memory** — the assistant writes structured notes after each task so future
  runs are smarter and more consistent.

---

## A realistic, satisfying first milestone
Tier 1 complete + `delegate_task` (Tier 2) + persistent memory (Tier 2). With just those, you can
say *"Jarvis, research X, build me a page about it, open it, and remember I prefer Y"* — and it
does, and it remembers. That already beats the tutorial video meaningfully. Everything else is
gravy you add when you want it.

## Guardrails that scale with capability
The more powerful the tier, the more the safety rules in `CLAUDE.md` matter:
- Email/messaging tools: **draft only**, never auto-send.
- Purchases/forms: always **confirm** first.
- Delegated/autonomous loops: **hard turn limits + timeouts + allow-listed tools** only.
- Memory: **local and private**; never transmit personal data it doesn't need to.
- No open-ended shell, ever, behind a microphone.
~~~

---

*End of brief. Hand this whole file to Claude Code with the kickoff prompt and you're off. Build one tool at a time, keep PROGRESS.md current, and have fun, sir.*
