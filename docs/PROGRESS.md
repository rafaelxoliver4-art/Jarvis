# PROGRESS — JARVIS single source of truth

> **This file is the BRIDGE** between Claude Code (the builder, in this repo) and Rafael's
> separate planning chat on Claude.ai. Rafael manually carries it between them. **If anything
> conflicts with this file, the file wins.** Keep it lean, scannable, and self-contained — a
> fresh reader with zero other context must be able to act on it instantly.

> Full operating model (who does what) lives in CLAUDE.md → Operating model.

> Mutual vigilance: both Claudes stay alert to each other's mistakes; nothing is 'done' until verified. Full rules in CLAUDE.md → Error-awareness & verification.

---

## ⚡ TL;DR — paste-ready status
- **Phase:** Phase 0 ✅ · Phase 1 ✅ · Phase 1.5 ✅ · Phase 2 ✅ · **Phase 3 IN PROGRESS** 🔧 — Tool #1 `get_system_info`: code complete, awaiting Rafael's dashboard registration + voice test
- **Next action:** **Rafael registers `get_system_info` in the ElevenLabs dashboard**, then Claude Code orchestrates the 30s voice test. Implementation is already done locally (psutil 7.2.2 installed + pinned; function added to `tools.py` with cross-platform 12-hour time, battery-omit-on-no-battery, `wrap_log()` applied at registration; imports + direct functional call both verified). See "Next action" section below for the exact dashboard text.
- **Blocked on:** Rafael's dashboard registration of `get_system_info`. **Working tree has uncommitted changes** (`requirements.txt` + `tools.py`) held for the post-voice-test Phase-3-Tool-#1 commit. PROGRESS.md interim-updated mid-phase for the planning chat.
- **Python decision:** ✅ venv on Anaconda Python 3.12.4. `elevenlabs==2.49.0`, `python-dotenv==1.2.2`, `PyAudio==0.2.14` installed and pinned in `requirements.txt`.
- **Repo:** `C:\Users\Rafael\OneDrive\Área de Trabalho\Jarvis\` · branch `main` · run `git log --oneline` for the commit trail.
- **Open questions:** none — all 7 resolved by the planning chat 2026-05-25 (see Decision log).

---

## 🧭 What JARVIS is (elevator)
A voice-controlled agentic personal assistant that runs on Rafael's Windows machine. Three layers: **ElevenLabs Agents** (speech-in / speech-out / turn-taking, cloud) → **a Claude model set in the ElevenLabs dashboard** (the brain that picks tools) → **local Python "client tools"** in this repo (the hands that actually act). For multi-step jobs, one tool — `delegate_task` — hands off to a **Claude Agent SDK** loop. Read `docs/ARCHITECTURE.md` before any structural change.

**⭐ North star (user directive, 2026-05-24):** *"JARVIS must keep improving itself the more we use it."* Treat persistent memory, procedural skills, and post-task self-reflection as load-bearing — not nice-to-haves. When choosing what to build next, prefer features that compound knowledge over one-shot capabilities.

---

## ⏭️ Next action

**Phase 3 — Core tools.** Five tools, built one at a time per CLAUDE.md working style. The Phase-2 round-trip pattern is now muscle memory: code → `wrap_log()` is automatic at registration → Rafael registers in dashboard → voice test → commit. Suggested build order:

1. **`get_system_info`** 🔧 ← **IN PROGRESS** (2026-05-25 evening). Code is complete; awaiting Rafael's dashboard registration + voice test. `psutil==7.2.2` installed and pinned. Function takes `parameters` (ignored), returns one short voice-friendly string like *"It's 9:02 PM on Tuesday. Battery's at 18% and on battery. CPU's at 22%, memory at 66%, sir."* Cross-platform 12-hour time (no `%-I`), battery clause omitted on machines with no battery, CPU sampled at `interval=0.5` for accuracy. Wrapped with `wrap_log()` at registration. `tools.py` imports clean, direct functional call verified.
2. **`save_file`** — skeleton already exists in `tools.py` (sandboxed to `./generated/`); only needs dashboard registration + voice test. Should be quick.
3. **`create_html_file`** — sibling of `save_file`; renders a small styled HTML page from a title/body and optionally opens it in the default browser.
4. **`search_web`** — DuckDuckGo via `langchain-community` (already in `requirements.txt` but not installed). Requires `pip install langchain-community` step. Returns text summary.
5. **`control_window`** — focus/minimize/close, allow-listed actions only. More complex (Windows-specific window-handle work). Last.

### Step-by-step for each tool (the standing pattern)
1. **(if needed) Install the dep** in the venv via `pip install`, then pin the exact version in `requirements.txt`.
2. **Implement the tool** in `tools.py` (or extend the existing skeleton). Must take a single `parameters` dict, return a short string, follow the Safety rules.
3. **Wrap with `wrap_log()` at registration time** (one-line change in the registry block).
4. **Verify imports still clean:** `python -c "import tools; print(type(tools.client_tools).__name__)"`.
5. **Pause for Rafael** to register the tool in the ElevenLabs dashboard (name + description + each param's name/type/description/required).
6. **Orchestrate a 30s voice test** (`python -u`, background timer, log-capture).
7. **Verify the wrap_log entry** in `logs/usage_log.jsonl` (outcome=`ok`, correct tool name, correct params, no secrets leaked).
8. **Rafael confirms** the observable side-effect happened (file created / browser opened / system info read aloud / etc.).
9. **Commit. Update PROGRESS.md.**

### What Rafael does next (UNBLOCK Tool #1 — `get_system_info`)
Register the tool in the ElevenLabs dashboard. Open the Jarvis agent → **Client Tools** section → **Add tool** → fill in:

| Field | Value |
|---|---|
| **Name** | `get_system_info` (exact — must match the registered name in `tools.py`) |
| **Description** | `Read out the current local time, day of the week, battery status (if applicable), and CPU and memory usage. Use this when the user asks about system status, current time or day, battery level, or computer performance.` |
| **Parameters** | **TRY ZERO PARAMS FIRST.** If the dashboard UI rejects saving without a param, add one optional dummy: name=`_unused`, type=`string`, description=`Not used.`, required=**No**. SDK source confirms the function side can ignore the dict entirely (the SDK auto-injects `tool_call_id` regardless), so the function works the same either way. |

Save the agent.

### What Claude Code does next (after Rafael confirms registration is saved)
1. Orchestrate a 30s live voice test (`python -u`, background timer, log capture). Rafael says *"Jarvis, what's my system status?"* (or any phrasing that should trigger the tool: "what time is it", "battery status", etc.).
2. Verify the wrap_log entry in `logs/usage_log.jsonl`: `outcome=ok`, `tool=get_system_info`, `params` shows `tool_call_id` (always) plus any registered params.
3. Rafael confirms Jarvis spoke the system info aloud (the actual time/battery/CPU readout, not just a generic acknowledgement).
4. Commit `tools.py` + `requirements.txt` + the PROGRESS.md wrap-up as one Phase-3-Tool-#1 commit. Set Next action = Tool #2 (`save_file`).

### Reminders / standing flags for Phase 3
- The ElevenLabs SDK auto-injects a `tool_call_id` field into every params dict (e.g., `"tool_call_id": "toolu_vrtx_..."`). Not a secret, not a leak — but it shows up in the wrap_log entries alongside our registered params. Don't be surprised when you see it.
- Watch for `wrap_log` `outcome=error` entries: that's our debugging gold. If anything goes wrong in Phase 3, the redacted-params + error-message in the log will usually point straight at the problem.

---

## ✅ Done
- **2026-05-25 — Phase 2 — `open_application` ✅ COMPLETE.** First real client-tool end-to-end round-trip verified live on Rafael's machine. Rafael registered the tool in the ElevenLabs dashboard (name=`open_application`, param=`app_name` string, available in Agent, status Live 100%). Claude Code orchestrated a 30-second supervised voice test via `python -u` launch + background timer + log capture. **Full verification:** `callback_user_transcript` fired ("Hey Jarvis. Open calculator."), the agent called `open_application(app_name="calculator")`, `wrap_log()` wrote a single record to `logs/usage_log.jsonl` (`outcome=ok`, `tool=open_application`, `params.app_name=calculator`, `duration_ms=199`), Calculator actually launched on Rafael's desktop (Rafael confirmed visually), Jarvis acknowledged in voice ("Of course, sir." / "Calculator's open, sir."), zero stderr errors. Agent then carried on conversationally (Rafael asked a math question, Jarvis answered correctly without re-calling the tool — multi-turn behaviour works). Confirmed observation: the ElevenLabs SDK auto-injects a `tool_call_id` field into the params dict (alongside our registered `app_name`); harmless metadata, not a secret, doesn't match any redaction substring, logged as-is. The Phase-2 pattern (code → wrap_log auto-applied → dashboard register → voice test → commit) is now muscle memory and will be reused for every tool from here.
- **2026-05-25 — Phase 1.5 — Tool-usage log ✅ COMPLETE** (commit `bbf74ed`). New `tool_logging.py` module exporting `wrap_log(tool_fn)`. Every client-tool call now appends one JSON object to `logs/usage_log.jsonl` with `ts_start`, `ts_end`, `duration_ms`, `tool`, `outcome` (`"ok"`|`"error"`), redacted `params`, and `error` (only on failure). **Thread-safe** via a module-level `threading.Lock()`. **Fail-open**: any logging-path exception is swallowed and the underlying tool's result (or exception) is still preserved. **Secrets-safe**: top-level param keys whose name (case-insensitive) contains any of `key, token, secret, password, passwd, api, auth, credential` are stored as `"<redacted>"`; non-sensitive values are truncated to 80 chars. Tool return values are NOT logged (privacy). The three existing skeleton tools (`open_application`, `save_file`, `delegate_task`) are wrapped at registration time in `tools.py`; the function definitions themselves are unchanged. Smoke-tested with a temp script (deleted after run): 7/7 assertions passed — happy-path with `api_key` redacted, forced `ValueError` re-raised intact (fail-open contract), errors logged with `outcome=error`. `logs/.gitkeep` tracks the folder; `logs/*.jsonl` is git-ignored so telemetry never gets committed.
- **2026-05-25 — Phase 1 — Voice loop ✅ COMPLETE.** Live audio test confirmed end-to-end working via **one** orchestrated run (Rafael did NOT separately run `python main.py` himself this session — the orchestrated test is the only live verification). Rafael first swapped the dashboard voice from IVC to a preset (resolving the earlier WebSocket `1002` error). Claude Code then orchestrated the live test: launched `main.py` via `python -u` (unbuffered stdout) with stdout/stderr redirected to log files, auto-terminated after 30 seconds. During that window Rafael spoke into his mic and listened to his speakers (his hardware, his Windows audio devices). Verified live: agent connects, plays first message "Good day, sir. How can I help?", transcribes Rafael's speech ("Hello Jarvis, can you hear me clearly?" → "What can you do for me right now?"), Claude responds in character ("Loud and clear, sir." / "I can help you open apps, files, or websites..."), TTS plays through speakers, callbacks (`callback_agent_response`, `callback_user_transcript`, `callback_agent_response_correction`) all fire, process exits cleanly with **zero stderr errors**. Phase 1 code path is proven; the `client_tools` wiring (empty registry) is in place ready for Phase 2.
- **2026-05-25 — Phase 1 build mechanics:** venv rebuilt 3.13.13 → Anaconda 3.12.4; `elevenlabs==2.49.0` + `python-dotenv==1.2.2` + `PyAudio==0.2.14` installed via prebuilt cp312 wheels (no Visual C++ Build Tools needed); `requirements.txt` pinned. SDK API verified against live `conversation.py` source on GitHub (`client_tools=` kwarg + `ClientTools` class + callbacks unchanged); no `main.py` edits needed. `tools.py` confirmed side-effect-light at import.
- **2026-05-24 — Phase 0 — Scaffold.** Project scaffolded at `C:\Users\Rafael\OneDrive\Área de Trabalho\Jarvis\` via the kickoff's alternative path (unzipped + flattened `starter/` → root). Python 3.13.13 `venv` created at `./venv` (no packages installed yet, per brief — will be rebuilt against 3.12 at Phase 1 start). `.env` populated with placeholders only — Rafael fills real keys.
- **2026-05-24 — Bridge convention encoded** in `CLAUDE.md` so future Claude Code sessions automatically inherit it (PROGRESS.md is single source of truth; file wins on conflicts; lean + scannable for zero-context readers; mandatory end-of-session ritual).
- **2026-05-24 — Python environment scan** completed: confirmed 3.12.4 (Anaconda) and 3.13.13 (Store) are the only Pythons available. No 3.11. Anaconda's interpreter is the chosen target for `venv`.

---

## 🔧 Known issues / WIP
- **🚧 Phase 3 Tool #1 mid-phase (2026-05-25 evening):** `get_system_info` code complete + wrapped + verified locally, but **working tree has uncommitted changes** (`tools.py` + `requirements.txt`) held for the post-voice-test commit. Awaiting (a) Rafael's dashboard registration of `get_system_info`, (b) orchestrated 30s voice test, (c) Rafael's audible confirmation. Single Phase-3-Tool-#1 commit then lands all changes together.
- **🔑 `ANTHROPIC_API_KEY` is still a placeholder in `.env`** — not needed until Phase 5 (`delegate_task` via Claude Agent SDK), but needs to be filled before that phase starts.
- **🎤 Audio-setup tip (observed during the Phase 1 test):** during the first ~10 seconds of the live run, Rafael's mic picked up the speakers, so JARVIS heard himself and started replying to his own echo. He noticed and pointed it out conversationally ("Might there be an audio feedback loop on your end?"). Standard fixes for next session: lower speaker volume, use headphones, or enable Windows microphone noise suppression. Not a code issue — purely a hardware/setup consideration that hit zero-cost for Phase 1 (the conversation recovered) but might matter for Phase 5's longer multi-step interactions.
- **🐍 Available Pythons on this machine** (verified 2026-05-24): 3.12.4 (Anaconda, used for Jarvis venv) and 3.13.13 (MS Store). No 3.11, no `py` launcher, no Visual C++ build tools — fine so far, since PyAudio's prebuilt cp312 wheel installed without compilation. Note if a future package needs to build from source.
- **🪪 Git identity is repo-local only** (`rafaelxoliver4@gmail.com` / `Rafael` in `.git/config`), not global. Change inside the Jarvis folder if a different name on commits is preferred.
- **☁️ OneDrive sync** can occasionally lock files during heavy operations (venv writes, `pip install`). If a future operation hits a weird file-lock error, pause OneDrive sync for a minute and retry. Right-click `Jarvis/` → "Always keep on this device" recommended to prevent offloading.

---

## 🧩 Tools — code & dashboard registration
A tool registered in code but NOT in the ElevenLabs dashboard is invisible to the agent. Both columns must be ✅ for a tool to actually work. **As of Phase 1.5, every registered tool is wrapped with `wrap_log()` automatically — calls land in `logs/usage_log.jsonl` from birth.**

| Tool | In code? | In ElevenLabs dashboard? | Phase | Notes |
|---|---|---|---|---|
| `open_application` | ✅ in `tools.py` (allow-list: chrome, vscode, calculator, notes, spotify) + wrapped with `wrap_log()` | ✅ registered 2026-05-25 (`app_name` string param) | Phase 2 ✅ | **Live-verified 2026-05-25**: agent → tool → calc.exe opens → log entry → voice ack |
| `save_file`        | ⚠️ skeleton + ✅ wrapped with `wrap_log()` (sandboxed to `./generated/`) | ❌ | Phase 3 | |
| `delegate_task`    | ⚠️ stub + ✅ wrapped with `wrap_log()` — returns a "not built yet" message | ❌ | Phase 5 | Full impl via Claude Agent SDK; needs `max_turns` + timeout + allow-listed tools |
| `search_web`       | ⏳ not started | ❌ | Phase 3 | DuckDuckGo via `langchain-community` |
| `create_html_file` | ⏳ not started | ❌ | Phase 3 | Sandboxed |
| `get_system_info`  | ✅ in `tools.py` (cross-platform 12-hour time, battery-omit-on-no-battery, `psutil==7.2.2`) + wrapped with `wrap_log()` | ⏸️ awaiting Rafael's registration | Phase 3 🔧 | Voice-friendly read-only status string; sampled CPU at `interval=0.5` for accuracy |
| `control_window`   | ⏳ not started | ❌ | Phase 3 | Allow-listed actions |
| `browse(task)`     | ⏳ not started | ❌ | Phase 4 | Playwright/MCP, not pixel-clicking |
| `remember` / `recall` | ⏳ not started | ❌ | Phase 6 | **North-star — load into context at session start** |

Legend: ✅ done · ⚠️ partial / skeleton only · ❌ missing · ⏳ not started yet

---

## 🗺️ Phase roadmap (the build — order confirmed 2026-05-25)
Build order: **`1 → 1.5 → 2 → 3 → 5 → 6 → 6.5 → 4 → 7`**. Compounding-knowledge features (delegation + memory + self-reflection) land before the browser.

- **Phase 0** ✅ Scaffold
- **Phase 1** ✅ Voice loop (no tools): `main.py` + ElevenLabs Conversation. Live audio confirmed 2026-05-25.
- **Phase 1.5** ✅ ⭐ **Tool-usage log** — `tool_logging.py` exports `wrap_log()`; all three skeleton tools wrapped at registration; thread-safe + fail-open + secrets-safe; logs go to `logs/usage_log.jsonl` (git-ignored). Completed 2026-05-25.
- **Phase 2** ✅ First real tool: `open_application` — live-verified 2026-05-25 (Calculator opened, Jarvis acknowledged in voice, wrap_log captured the call).
- **Phase 3** ⏭️ Core tools, one at a time: **`get_system_info`** (start here — psutil read-only) → `save_file` → `create_html_file` → `search_web` → `control_window`
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
- **2026-05-25 (evening)** — **Zero-param Client Tools: SDK-confirmed supported on function side; dashboard UI behavior verified empirically per-tool.** WebFetch'd the ElevenLabs SDK source: `ClientTools.register()` accepts any handler with `Callable[[dict], ...]` signature; the SDK always invokes with a dict containing at least `tool_call_id` (auto-injected). So registering a tool with zero declared params is fine functionally — the function just ignores the dict. The ElevenLabs **dashboard UI** behavior for zero-param registration is undocumented, so the standing pattern for read-only / no-input tools is: try zero params first; if the UI rejects, fall back to one optional dummy param (e.g., `_unused` string, not required). Applied to `get_system_info` and all future no-input tools.
- **2026-05-25 (late)** — **Phase 2 verified LIVE: `open_application` end-to-end.** Same orchestration pattern as Phase 1 (Claude Code launched `main.py` via `python -u`, redirected stdout/stderr + snapshotted log line count, 30s background timer, auto-kill). Rafael said *"Hey Jarvis. Open calculator."* — agent transcribed correctly, called `open_application(app_name="calculator")`, `wrap_log()` captured one record (`outcome=ok`, `duration_ms=199`, no errors), Calculator launched on Rafael's desktop (visually confirmed), agent acknowledged in voice. Multi-turn conversation continued cleanly afterward (Rafael asked a math question; agent answered correctly without re-calling the tool — shows the agent's conversational context is intact across tool calls). **Phase-2 round-trip pattern is now reusable muscle memory for the remaining tools.**
- **2026-05-25 (late)** — **ElevenLabs SDK auto-injects `tool_call_id` into the params dict** (observed: `"tool_call_id": "toolu_vrtx_01BNkWDaK7yLwcASZnyrnewQ"` alongside our registered `app_name`). The `toolu_vrtx_` prefix suggests Anthropic-via-Vertex under the hood at ElevenLabs. Not a secret, harmless metadata, useful for correlating client-side logs with the cloud agent. Does NOT match any of our 8 redaction substrings, so it's logged as-is. Expect this in every wrap_log entry from now on; no code change required.
- **2026-05-25 (late)** — **Phase 1.5 tool-usage log design contracts (locked in).** Three non-negotiables for `wrap_log()`: (1) **Thread-safe** via a single module-level `threading.Lock()` — sufficient for the single-process voice loop; do NOT upgrade to a queue without a real reason. (2) **Fail-open** — any exception inside the logging path is swallowed; the underlying tool's result or exception is always preserved. Logging must never break or block a tool action. (3) **Secrets-safe redaction rule:** for each top-level param key, if the key name (case-insensitive) contains any of `key`, `token`, `secret`, `password`, `passwd`, `api`, `auth`, `credential`, the value is replaced with `"<redacted>"`. Non-sensitive values are str-coerced and truncated to 80 chars. Greedy substring matching is acceptable — over-redaction beats leakage. Top-level only; nested dicts not recursed (flag for future tools with nested params).
- **2026-05-25 (late)** — **Tool return values are NOT logged.** Only outcome (`"ok"` | `"error"`) and error message on failure. Privacy: tool returns can contain personal data. If we ever need result-content for debugging, add a separate `result_summary` field with the same redaction rule (deferred — not needed yet).
- **2026-05-25 (evening)** — **ElevenLabs agent switched from Public to Private (auth-enabled and published).** Rafael flipped the agent's privacy in the dashboard after the live Phase 1 verification. Removes the remote-trigger risk that would otherwise have been a Phase 2 blocker once `open_application` is registered. No code change required.
- **2026-05-25 (evening)** — **Phase 1 verified LIVE — single orchestrated test, no Rafael-own run.** Sequence: (1) Rafael swapped the dashboard voice from IVC → preset library voice, resolving the WebSocket `1002` close from the earlier headless smoke test. (2) Claude Code then orchestrated the *only* live verification of this session: started `main.py` via `python -u` (unbuffered stdout), redirected stdout/stderr to log files, ran for exactly 30 seconds before auto-terminating. (3) During that 30-second window Rafael spoke into his mic and listened to his speakers; he **did not separately run `python main.py` himself** in this session. The captured transcript confirmed full round-trip: agent's first message played, Rafael's speech transcribed correctly, Claude responded in butler-character ("Loud and clear, sir"), TTS played through speakers, zero stderr errors. **Phase 1 code path is proven end-to-end on real hardware via this one orchestrated test.** `client_tools` wiring (empty registry) is in place ready for Phase 2's first real tool.
- **2026-05-25** — **`python -u` (unbuffered stdout) is required when launching `main.py` from a non-interactive shell** (e.g. Claude Code orchestration). Without it, Python's default block buffering hides "JARVIS is listening" and the callback prints until the process exits — making live monitoring impossible. For Rafael's own `python main.py` runs in a TTY this isn't needed (stdout is line-buffered automatically), but it's the standard pattern for any future orchestration / CI / log-capture work.
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
