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
