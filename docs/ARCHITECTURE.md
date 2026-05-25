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
