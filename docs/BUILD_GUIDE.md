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
