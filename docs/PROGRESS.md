# PROGRESS — JARVIS single source of truth

> **This file is the BRIDGE** between Claude Code (the builder, in this repo) and Rafael's
> separate planning chat on Claude.ai. Rafael manually carries it between them. **If anything
> conflicts with this file, the file wins.** Keep it lean, scannable, and self-contained — a
> fresh reader with zero other context must be able to act on it instantly.

> Full operating model (who does what) lives in CLAUDE.md → Operating model.

> Mutual vigilance: both Claudes stay alert to each other's mistakes; nothing is 'done' until verified. Full rules in CLAUDE.md → Error-awareness & verification.

---

## ⚡ TL;DR — paste-ready status
- **Phase:** Phase 0 ✅ done · **Phase 1 — Voice loop IN PROGRESS** 🔧 (code path verified end-to-end on 2026-05-25; final live audio test deferred — see Next action).
- **Next action:** Rafael swaps the agent's voice in the ElevenLabs dashboard from the current Instant Voice Clone (IVC) to a preset library voice (e.g., Charlie / Brian / Daniel / George), then — when his speakers are available — Claude Code re-runs the smoke test and (ideally) Rafael also runs `python main.py` and confirms live audio. See "Next action" section below for the full procedure.
- **Blocked on:** Rafael's dashboard voice swap (IVC not on current plan — see WIP) AND a future moment when Rafael's speakers are available for live audio test. Rafael may delay the audio test; the dashboard fix is the only thing strictly required to unblock the next smoke test.
- **Python decision:** ✅ **venv rebuilt** against Anaconda's Python 3.12.4 on 2026-05-25 (was 3.13.13). `elevenlabs==2.49.0`, `python-dotenv==1.2.2`, `PyAudio==0.2.14` installed and pinned in `requirements.txt`.
- **Repo:** `C:\Users\Rafael\OneDrive\Área de Trabalho\Jarvis\` · branch `main` · run `git log --oneline` for the commit trail.
- **Open questions:** none — all 7 resolved by the planning chat 2026-05-25 (see Decision log).

---

## 🧭 What JARVIS is (elevator)
A voice-controlled agentic personal assistant that runs on Rafael's Windows machine. Three layers: **ElevenLabs Agents** (speech-in / speech-out / turn-taking, cloud) → **a Claude model set in the ElevenLabs dashboard** (the brain that picks tools) → **local Python "client tools"** in this repo (the hands that actually act). For multi-step jobs, one tool — `delegate_task` — hands off to a **Claude Agent SDK** loop. Read `docs/ARCHITECTURE.md` before any structural change.

**⭐ North star (user directive, 2026-05-24):** *"JARVIS must keep improving itself the more we use it."* Treat persistent memory, procedural skills, and post-task self-reflection as load-bearing — not nice-to-haves. When choosing what to build next, prefer features that compound knowledge over one-shot capabilities.

---

## ⏭️ Next action

> **Where we are mid-Phase 1:** the code path is fully built and verified — venv on 3.12.4, deps installed, SDK imports + `Conversation` constructor signature verified against the live source, headless smoke test on 2026-05-25 confirmed: `main.py` starts cleanly, `.env` loads, the WebSocket connects, the agent session is created (conversation ID issued by the server), `start_session()` returns successfully. The smoke test was then terminated by the server with WebSocket close code `1002` and the message *"Instantly cloned voices are not available on your current plan. Please upgrade your subscription."* — i.e. the agent's voice in the dashboard is an Instant Voice Clone that the current plan can't use for TTS. **The code is correct; the remaining gap is a dashboard config tweak plus a live audio test.**

### What Rafael does next (UNBLOCK for the next smoke test)
- [ ] **Swap the agent's voice in the ElevenLabs dashboard.** Open the Jarvis agent → Voice section → pick a **preset library voice** (NOT one under "My Voices" → "Cloned"). Recommended candidates that match the deep-British-butler feel: **Charlie** (if available on your plan), **Brian**, **Daniel**, **George**. Save the agent.
- [ ] *(Optional but recommended while you're in the dashboard)* Flip the agent from **Public → Private** so it can't be invoked by anyone with the Agent ID. Required before Phase 2 lands the first real tool (`open_application`); fine to do now.
- [ ] *(Optional)* Turn on speakers + mic when ready for the live audio test. Rafael may defer this — the next smoke test does not require it.

### What Claude Code does next (after Rafael confirms the voice was swapped)
1. Re-run the **headless smoke test** of `main.py` (same 25-second window, capturing stdout/stderr). Success signal = no `1002` close, no traceback, process runs until killed.
2. If the smoke test passes cleanly, report back; **then Rafael runs `python main.py` himself** when his audio is available to verify the full mic-in / speaker-out round-trip ("Hello Jarvis" → audible response).
3. **Only after Rafael confirms live audio works**, do the Phase 1 wrap-up: move Phase 1 → Done, set Next action = Phase 1.5 — tool-usage log, commit.

---

## ✅ Done
- **2026-05-25 — Phase 1 partial — code path verified end-to-end (final live audio test pending).** Old 3.13.13 venv deleted; new venv created against Anaconda Python 3.12.4. Installed `elevenlabs==2.49.0` + `python-dotenv==1.2.2` + `PyAudio==0.2.14` (cp312 prebuilt wheel — no C compile needed; no Visual C++ Build Tools required after all). `requirements.txt` pinned to those exact versions for reproducibility. SDK API verified against live `conversation.py` source on GitHub: `client_tools=` kwarg still accepted, `ClientTools` class still exported from `elevenlabs.conversational_ai.conversation`, all three callbacks used by the starter still in the constructor signature → **no changes needed to `main.py`** (kept the `client_tools` wiring per the planning chat's failure-isolation argument). `tools.py` confirmed side-effect-light at import (only `os.makedirs("./generated/", exist_ok=True)`). Headless smoke test ran: WebSocket connected, conversation session created server-side (got a `conv_…` ID), `start_session()` returned cleanly, "JARVIS is listening" printed; server then closed with `1002` due to the IVC voice (see WIP). No code bug — pipeline proven.
- **2026-05-24 — Phase 0 — Scaffold.** Project scaffolded at `C:\Users\Rafael\OneDrive\Área de Trabalho\Jarvis\` via the kickoff's alternative path (unzipped + flattened `starter/` → root). Python 3.13.13 `venv` created at `./venv` (no packages installed yet, per brief — will be rebuilt against 3.12 at Phase 1 start). `.env` populated with placeholders only — Rafael fills real keys.
- **2026-05-24 — Bridge convention encoded** in `CLAUDE.md` so future Claude Code sessions automatically inherit it (PROGRESS.md is single source of truth; file wins on conflicts; lean + scannable for zero-context readers; mandatory end-of-session ritual).
- **2026-05-24 — Python environment scan** completed: confirmed 3.12.4 (Anaconda) and 3.13.13 (Store) are the only Pythons available. No 3.11. Anaconda's interpreter is the chosen target for `venv`.

---

## 🔧 Known issues / WIP
- **🎙️ Agent's voice in the dashboard is an Instant Voice Clone (IVC) — current plan can't use it.** Smoke test 2026-05-25 was killed by the server with WebSocket close `1002`: *"Instantly cloned voices are not available on your current plan. Please upgrade your subscription."* Fix: Rafael swaps the voice in the ElevenLabs dashboard to a preset library voice (Charlie / Brian / Daniel / George recommended). Once swapped, Claude Code re-runs the headless smoke test to confirm.
- **🔊 Live audio test deferred** — Rafael's speakers were off during the 2026-05-25 attempt. Headless smoke test was used as a partial substitute (proved everything up to TTS). The final mic-in / speaker-out round-trip still needs Rafael's hardware. Phase 1 cannot be marked Done until that happens.
- **🌐 ElevenLabs agent is currently set to Public.** Fine for Phase 1 testing on Rafael's machine, but **must be switched to Private before Phase 2** lands the first real tool (`open_application`). A Public agent + a tool that opens applications = anyone with the Agent ID could trigger commands on Rafael's box. Easy to flip in the dashboard.
- **🔑 `ANTHROPIC_API_KEY` is still a placeholder in `.env`** — not needed until Phase 5 (`delegate_task` via Claude Agent SDK), but needs to be filled before that phase starts.
- **🐍 Available Pythons on this machine** (verified 2026-05-24): 3.12.4 (Anaconda, used for Jarvis venv) and 3.13.13 (MS Store). No 3.11, no `py` launcher, no Visual C++ build tools — fine for now, since PyAudio's prebuilt cp312 wheel installed without compilation. Note if a future package needs to build from source.
- **🪪 Git identity is repo-local only** (`rafaelxoliver4@gmail.com` / `Rafael` in `.git/config`), not global. Change inside the Jarvis folder if a different name on commits is preferred.
- **☁️ OneDrive sync** can occasionally lock files during heavy operations (venv writes, `pip install`). If a future operation hits a weird file-lock error, pause OneDrive sync for a minute and retry. Right-click `Jarvis/` → "Always keep on this device" recommended to prevent offloading.

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

## 🗺️ Phase roadmap (the build — order confirmed 2026-05-25)
Build order: **`1 → 1.5 → 2 → 3 → 5 → 6 → 6.5 → 4 → 7`**. Compounding-knowledge features (delegation + memory + self-reflection) land before the browser.

- **Phase 0** ✅ Scaffold
- **Phase 1** 🔧 IN PROGRESS — Voice loop (no tools): `main.py` + ElevenLabs Conversation. Code path verified 2026-05-25; awaiting dashboard voice swap + live audio test.
- **Phase 1.5** ⭐ **Tool-usage log** — `logs/usage_log.jsonl` + a `wrap_log()` helper every tool wraps with (timestamp, tool name, short param summary, outcome, duration). **Secrets-safe** — never log `.env` values or sensitive params. Done before Phase 2 so every real tool is logged from birth, giving Phase 6.5 full telemetry to learn from.
- **Phase 2** First real tool: `open_application` (learn the pattern)
- **Phase 3** Core tools: `search_web`, `save_file`, `create_html_file`, `get_system_info`, `control_window`
- **Phase 5** ⭐ Reasoning & delegation: `delegate_task` via Claude Agent SDK. Uses the SDK's built-in web search + file tools, so it's useful even before our `browse` tool exists; `browse` plugs into its allow-list later.
- **Phase 6** ⭐ Persistent memory: `remember`/`recall`, loaded at session start. **v1 store format = JSON Lines** (append-only `.jsonl`, one record per line, each tagged `type` = `"fact"` | `"reflection"`). Clean upgrade path to a Chroma vector store later.
- **Phase 6.5** ⭐ **Self-improvement loop** (procedural memory only — NOT runtime self-modification): after every `delegate_task`, write a structured reflection note; future delegations include relevant notes in the system prompt. Reflection-note schema (refinable at the phase): `{date (ISO 8601), tags[] (for retrieval), goal (one sentence), tools_used[], outcome (succeeded|partial|failed), what_helped, what_to_avoid, advice_for_future_self}`. **The feature that delivers the north star.**
- **Phase 4** Browser control: `browse(task)` — **provisional** lean toward Playwright (full control, mature, no third-party-MCP dependency); **re-validate at phase start** since the browser-automation landscape moves fast.
- **Phase 7** Polish: **push-to-talk first** (wake word deferred; if added later, lean OpenWakeWord over Porcupine), screen vision, startup launch, tool router

⭐ = directly serves the "JARVIS improves itself the more we use it" directive.

---

## ❓ Open questions for the planning chat
None currently — all resolved (see Decision log).

---

## 🧠 Decision log (newest first)
- **2026-05-25** — **SDK API verified against live source** before any Phase 1 changes. Fetched `Conversation.__init__` from `elevenlabs/elevenlabs-python` on GitHub `main`: `client_tools: Optional[ClientTools] = None` kwarg still present, `ClientTools` class still defined inside `elevenlabs.conversational_ai.conversation`, all three callbacks used by the starter (`callback_agent_response`, `callback_agent_response_correction`, `callback_user_transcript`) still accepted. Public docs intro page no longer shows `client_tools=` in its canonical example — that's a docs simplification, not an API removal. **No `main.py` changes were needed.**
- **2026-05-25** — **Kept the `client_tools` wiring in Phase 1 `main.py`** per the planning chat's failure-isolation argument: each phase adds exactly one new variable; removing now + re-adding in Phase 2 would make Phase 2 the first test of the wiring AND the first real tool AND dashboard registration all at once. Wiring is a no-op at runtime in Phase 1 (no tools registered in dashboard), so cost is zero.
- **2026-05-25** — **Phase 1 verification strategy = headless smoke test when Rafael's speakers unavailable.** Constraint: Claude Code has no microphone or speakers, so cannot directly confirm audio playback. Smoke test (run `main.py` for ~25s with stdout/stderr captured, then kill) proves the code path up to TTS — start-up, `.env` loading, SDK client construction, WebSocket connection, session creation, first-message callback — but NOT actual sound out of speakers or mic capture. Per the vigilance rule, Phase 1 stays "in progress" until Rafael's live hardware test confirms the round-trip end-to-end.
- **2026-05-25** — **`requirements.txt` pinned to exact installed versions** for reproducibility: `elevenlabs[pyaudio]==2.49.0`, `python-dotenv==1.2.2`. PyAudio 0.2.14 installed via prebuilt cp312 wheel — confirmed no Visual C++ Build Tools needed on this machine. Other libs (`psutil`, `langchain-community`, `claude-agent-sdk`) stay unpinned until their respective phases.
- **2026-05-25** — **Build order confirmed (Q1):** 1 → 1.5 → 2 → 3 → 5 → 6 → 6.5 → 4 → 7. Compounding-knowledge features (delegation, memory, self-reflection) land before the browser. Safe because delegate_task uses the Claude Agent SDK's built-in web search + file tools, so it's useful without our browse tool; browse plugs into its allow-list later.
- **2026-05-25** — **Tool-usage log = new Phase 1.5 (Q5):** right after the voice loop works, before the first real tool. Minimal logs/usage_log.jsonl + a wrap_log() helper every tool wraps with (timestamp, tool name, short param summary, outcome, duration). MUST be secrets-safe — never log .env values or sensitive params. Done before Phase 2 so every tool is logged from birth and Phase 6.5 has full telemetry; not before Phase 1 (no tools to log yet — prove the pipeline first).
- **2026-05-25** — **delegate_task stays UNREGISTERED in the dashboard until Phase 5 (Q4).** Registering a stub would make the agent call a dead tool; let it reason conversationally instead. Register only when it actually works.
- **2026-05-25** — **Phase 6.5 scoped to procedural memory only, NOT runtime self-modification (Q2).** JARVIS writes post-task reflection notes future runs read; it does NOT edit its own code/tools live (that stays a supervised Claude Code task Rafael approves). Reflection-note schema (refinable at Phase 6.5): {date (ISO 8601), tags[] (for retrieval), goal (one sentence), tools_used[], outcome (succeeded|partial|failed), what_helped, what_to_avoid, advice_for_future_self}. Added tags vs the strawman so recall can fetch relevant notes by task type.
- **2026-05-25** — **Memory v1 format = JSON Lines (Q3).** Append-only .jsonl, one record per line, each tagged type ("fact" | "reflection"). Simplest robust option, trivial to append/parse, clean upgrade path to a Chroma vector store. Obsidian/markdown dual-use deferred to a later "export memory to markdown" tool rather than making the primary store markdown.
- **2026-05-25** — **Browser approach = PROVISIONAL lean Playwright, finalize at Phase 4 (Q6).** Full control, mature, no third-party-MCP dependency, composes into delegate_task's allow-list. Marked provisional — re-run a fresh research pass at Phase 4 since the browser-automation/MCP landscape moves fast.
- **2026-05-25** — **Wake word deferred; start with push-to-talk (Q7).** Always-on wake word adds false-triggers and complexity for marginal early benefit. If added later, lean OpenWakeWord (open source) over Porcupine (commercial). Low-priority Phase 7.
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
  - Vector-store semantic memory upgrade from JSON Lines (Chroma or similar) — the Phase 6 v1 format is `.jsonl` with a clean upgrade path here.
- Calendar + email (draft-only) via APIs or MCP servers.
- Multi-agent orchestration (specialised research / email / calendar sub-agents under one Jarvis).
- Proactive / scheduled tasks (morning briefing, reminders, background work overnight).
- Tool router once we exceed ~15–20 tools (avoid context rot from too many visible tools).
- Smart-home integrations (if compatible hardware).
