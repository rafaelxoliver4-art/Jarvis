# CONTEXT — JARVIS project briefing for new sessions

> **Read this BEFORE anything else.** This file is the "from scratch" briefing
> for any new conversation — whether you're a Claude Code session opening this
> repo, or a Claude.ai planning chat receiving a context upload. It captures
> what we're building, how we work, and what we've learned, so a new session
> can pick up exactly where the project left off without reconstructing the
> mental model from scratch.
>
> **For Rafael:** upload this file (or paste its contents) at the start of every
> new conversation with either Claude — Claude Code OR the planning chat. Pair
> it with `docs/PROGRESS.md` (the current state) so the new conversation has
> both the project's durable knowledge (this file) and its current TODO
> (PROGRESS.md).

---

## 1. What we're building

**JARVIS** is a voice-controlled agentic personal assistant running on Rafael's
Windows machine. You speak; it understands; it *does things* — opens apps,
creates files, searches the web, eventually browses, remembers, and delegates
multi-step tasks autonomously.

It is **not** a chatbot that describes how to do something. It's an agent with
hands — concrete actions on a real computer, guarded by structural safety
rules.

### Three-layer architecture (foundational mental model)

1. **ElevenLabs Agents (cloud)** — speech-to-text, text-to-speech (the Jarvis
   voice), and turn-taking. The hard speech machinery, hosted for us.
2. **A Claude model (brain, set in the ElevenLabs dashboard)** — understands
   intent and decides *which tool to call* with *what arguments*.
3. **Local Python "client tools" (hands)** — in `tools.py`, functions that
   actually do things on the machine. **This is where we add capability** —
   most "make Jarvis do more" work is just adding small, safe tools here.

Plus a fourth, special layer (Phase 5): **`delegate_task`** — for multi-step
autonomous jobs. This tool spawns a **Claude Agent SDK** loop that plans and
executes many steps, then returns a summary.

### ⭐ North star (immutable, user directive 2026-05-24)

*"JARVIS must keep improving itself the more we use it."*

Persistent memory, procedural skills, and post-task self-reflection are
load-bearing — not nice-to-haves. When picking what to build next, **prefer
features that compound knowledge over one-shot capabilities.**

**End goal (2026-05-30):** the self-improvement north star serves a purpose — JARVIS exists to turn Rafael's ideas into shipped products (apps, sites, ultimately a business), orchestrating his Claude ecosystem (Claude Code, the API, `delegate_task`'s Agent SDK loop). `delegate_task` (Phase 5) is the first brick: speak a build goal → autonomous Claude coding loop executes → reports back. Read the roadmap through "does this help Rafael ship?" Realistic line: JARVIS accelerates/executes; the idea, judgment, and product decisions are Rafael's.

### Where the project is (high level — read PROGRESS.md for detail)

```
Phase 0    ✅ Scaffold
Phase 1    ✅ Voice loop (main.py + ElevenLabs Conversation)
Phase 1.5  ✅ Tool-usage log (wrap_log + logs/usage_log.jsonl)
Phase 2    ✅ First real tool: open_application
Phase 3    ✅ COMPLETE (2026-05-30) — All 5 core tools live-verified
           ✅ get_system_info, ✅ save_file, ✅ create_html_file,
           ✅ search_web, ✅ control_window
Phase 5    ⭐ Reasoning & delegation (delegate_task via Claude Agent SDK) ← NEXT
Phase 6    ⭐ Persistent memory (remember / recall)
Phase 6.5  ⭐ Self-improvement loop (procedural memory, NOT runtime self-mod)
Phase 4    Browser control (Playwright/MCP, deferred per north-star reorder)
Phase 7    Polish (push-to-talk first; wake word deferred)
```

> Phase order reflects a deliberate reorder (decided 2026-05-25): delegation, memory, and self-reflection (5/6/6.5) ship before browser control (4) because compounding-knowledge features serve the north star directly; one-shot capabilities can wait.

⭐ = directly serves the self-improvement north star.

---

## 2. How we work — the operating model

This project is built by a **three-part Claude team with Rafael as the human bridge:**

- **Planning chat** (Claude.ai project) = **architect.** Researches, designs
  features, weighs decisions, writes the build prompts Rafael pastes into
  Claude Code.
- **Claude Code** (in this repo) = **builder.** Implements, runs, debugs,
  commits/pushes.
- **JARVIS Research** (separate Claude.ai project) = **researcher (sidecar).**
  Does focused, current, web-sourced research (alpha-SDK behavior, library
  choices, best practices, cost/security) and returns decision-ready proposals
  (adopt / consider / reject). It **informs and adjusts** the plan; it does NOT
  hijack the timeline or the build order.
- **Rafael** = **bridge + decision-maker.** Carries `docs/PROGRESS.md` /
  `CONTEXT.md` and research findings between all three; does the human-only
  steps (accounts, API keys, the ElevenLabs dashboard, running commands, voice
  testing); makes the final calls.

The Claudes **cannot talk directly.** Rafael manually carries `docs/PROGRESS.md`
(and findings) between them. **If anything ever conflicts with PROGRESS.md,
PROGRESS.md wins.**

**Claude Code can REQUEST a research pass.** When Code hits a question it can't
safely answer from memory — alpha-SDK behavior, a library maintenance/security
question, an "is there a better approach?" — it should flag it explicitly in
its report as **"worth a research pass"** so Rafael can carry it to JARVIS
Research. Code participates by *surfacing* these, not by guessing.

### Workflow per session

1. **START** — read `CLAUDE.md` and `docs/PROGRESS.md`. State the current
   phase and the single Next action.
2. **PLAN** — for any non-trivial change, propose a plan first; surface
   risks; wait for approval; then build.
3. **VERIFY** — after every change, *run / read / open* to confirm it
   worked. **"Done" requires evidence, not vibes.**
4. **END** — update `PROGRESS.md` (move finished items to Done, write the
   next single clear Next action, log decisions, note WIP/broken). Commit.
   **Never skip the wrap-up — treat omission as a failure.**

### Mutual vigilance

Two LLMs can compound mistakes — a plausible-but-wrong assumption from one
gets executed confidently by the other. Treat the planning chat's prompts
as a smart peer's *recommendations*, not commands — sanity-check each
against the current code, the architecture, and the safety rules. If a
prompt looks wrong, **flag it BEFORE building.** Full rules in `CLAUDE.md`
→ "Error-awareness & verification."

---

## 3. Standing conventions (lessons we forged, now baked in)

These were each learned from real test runs and bug-finds. Full context
for each lives in `docs/PROGRESS.md` → Decision log.

### Safety rules (NON-NEGOTIABLE)

- **File writes go ONLY into `./generated/`.** Use `_safe_path()` in
  `tools.py` — rejects `..`, `/`, `\`, absolute paths, escape attempts.
  Reuse it for any file-writing tool.
- **App / window / system actions use ALLOW-LISTS.** Unknown target →
  polite refusal, no execution.
- **NO open-ended shell tool.** Voice + arbitrary shell = remote-code-exec
  risk.
- **Irreversible/sensitive actions** (delete, send, buy, submit form)
  RETURN a confirmation request — never execute directly.
- **Never read, print, log, or transmit `.env` values, secrets, or API
  keys.**
- **`delegate_task` (Phase 5)** must run with hard `max_turns` + timeout +
  allow-listed tools only.

### The per-tool build pattern (standing loop)

For every new tool from Phase 2 onward:

1. *(if needed)* `pip install` + pin the dep in `requirements.txt`
2. Write the function in `tools.py` — takes a single `parameters` dict,
   returns a short voice-friendly string, follows the Safety rules
3. **Wrap with `wrap_log()` at registration** (every tool is auto-logged
   to `logs/usage_log.jsonl`)
4. Verify imports clean: `python -c "import tools; print(type(tools.client_tools).__name__)"`
5. Run a **direct-invocation test** (bypass the ElevenLabs agent — exercises
   the code-layer safety; voice tests can be intercepted at the prompt
   layer and miss real bugs)
6. Hand off dashboard registration text to Rafael
7. After Rafael registers, orchestrate a 30s voice test
   (`python -u`, background timer, log-capture)
8. Rafael confirms the observable side-effect actually happened
9. Commit + update `PROGRESS.md`

### Dashboard configuration gotchas

- **"Wait for response" must be ENABLED for return-valued tools.** Without
  it, the cloud agent doesn't wait for the SDK's response and uses a
  fallback *"called successfully"* string → the agent says *"tool ran but
  no readable data."* Fire-and-forget tools (like `open_application`)
  correctly work with it OFF.
- **Response timeout defaults to 1 SECOND.** Bump for any tool slower than
  ~700ms. Standing recommendations: `save_file`=5s, `create_html_file`=5s,
  `search_web`=10–15s (verified live 2026-05-26 with a real DDG round-trip
  of 2072 ms), future `delegate_task`=30s.
- **Zero-param tools are supported** — the dashboard accepts tools with no
  parameters; the SDK auto-injects `tool_call_id`. No dummy param needed.

### Code patterns

- **`python -u` (unbuffered stdout)** is required when orchestrating
  `main.py` from a non-interactive shell. Without it, prints get
  block-buffered and "JARVIS is listening" never appears in captured logs.
  For Rafael's own TTY runs this isn't needed.
- **`wrap_log` design contracts:** thread-safe (module-level
  `threading.Lock`); fail-open (logging errors swallowed); secrets-safe
  (substring redaction on params with key names matching `key`, `token`,
  `secret`, `password`, `passwd`, `api`, `auth`, `credential`); tool return
  values are NOT logged (privacy).
- **Multi-tool chaining works.** The LLM agent composes tools across
  multi-turn conversation and asks permission before consequential
  follow-ups. Confirmed live during Phase-3-Tool-#3.
- **Defense in depth.** A safety-test via voice may be intercepted by the
  prompt-layer (LLM refuses based on tool description) before reaching
  the code-layer. ALWAYS pair voice tests with direct-invocation tests
  for any tool with structural safety.
- **Verifiability constraint on Phase 6.5 self-improvement.** Reflection-note signal is strongest on objectively verifiable fields (tools_used, outcome, observable side-effect) and weakest on subjective quality ("was that briefing helpful?"). When designing reflection retrieval, lean on what's verifiable.
- **Registry-aware Windows app launching: `cmd /c start "" target`, NOT `Popen(target, shell=True)`.** The bare-exe form silently fails when `target` isn't on Windows PATH — Popen doesn't raise because it successfully launches a shell; the shell THEN can't find the exe and leaks an error to stderr that the calling function never sees. Result: tool returns success while nothing happens. The `start` command resolves apps via the App Paths registry and reliably finds installed apps. The empty `""` is the window-title placeholder `start` expects when the first quoted arg is the program path. Apply this pattern to any Windows app-launch code.
- **Cross-locale window-title matching: case-insensitive partial substring, with multiple patterns for non-cognate localized names.** Rafael's machine is PT-BR. Windows like Calculator (en) / Calculadora (pt) share the substring "calc" — a single case-insensitive substring match catches both. Non-cognate pairs like Notepad (en) / Bloco de Notas (pt) need an explicit list of alternative patterns. Verified empirically — the test Calculator opened with title `'Calculadora'` and was correctly matched by the `"calc"` pattern. Apply to any Windows window-control or window-search code.
- **Post-action verification beats trusting silent-success from OS-wrapper libraries.** Discovered in Phase-3-Tool-#5's first voice test: `pywinctl.activate()` and `.minimize()` return silently even when Windows refused the action (e.g., `SetForegroundWindow` anti-focus-stealing protection blocks focus; UWP multi-handle Calculator was picking the wrong window). The function reported `outcome=ok` while nothing visibly happened. **Standing rule:** after any state-mutating call into a Win32 / OS wrapper library, check the post-state on the **same object reference** (e.g., `target.isMinimized` / `target.isActive`) and report honestly if the action didn't take. Apply to any future tool that wraps OS-level state changes.
- **UWP apps open multiple window handles — pick the largest by area.** Calculator UWP opens 4 windows: the main UI + 3 hidden helpers. `getWindowsWithTitle("calc")` returns all 4; picking the first match silently mutates a wrong handle. Heuristic: `max(matches, key=lambda w: w.size.width * w.size.height)` — the main UI is always visibly the largest. Empirically verified against PT-BR `Calculadora`. **Standing rule:** any future window-control tool must use this heuristic, not first-match.
- **Minimize+restore as a focus workaround for Windows anti-focus-stealing.** When `SetForegroundWindow` is blocked (common — Windows aggressively protects focus from background apps), a minimize→restore cycle reliably brings a window forward without tripping the restriction. Standard fallback pattern for any focus-bringing code on Windows.

### Claude Agent SDK lessons (Phase 5 — verified on the new machine 2026-05-31)
- **The SDK needs no separate Node.js install on Windows.** `claude-agent-sdk 0.2.87` ships a working bundled CLI that runs without system Node (no `CLINotFoundError`, no init-hang). Don't add a Node step to setup docs.
- **Deny-by-default is layered, and `can_use_tool` is the *secondary* layer.** `disallowed_tools` removes a tool from the model's context entirely (primary, config-layer block — agent never attempts it). `can_use_tool` only fires when a call evaluates to "ask", so it's never invoked for already-allowed/denied/`disallowed_tools` cases; it also requires a streaming-mode prompt (`AsyncIterable[dict]`). **To observe/gate EVERY tool call, use a `PreToolUse` hook.** Design `delegate_task` safety as `disallowed_tools` + `can_use_tool` + (optionally) a `PreToolUse` hook. `permission_mode="dontAsk"` and `tools=[]` are additional hard levers.
- **`load_dotenv(override=True)` when a key feeds a subprocess.** The SDK's CLI authenticates from the `ANTHROPIC_API_KEY` *environment variable*. An empty ambient var can shadow `.env` because `load_dotenv()` defaults to `override=False`. Use `override=True` (or otherwise guarantee the real key reaches the subprocess). `main.py` uses plain `load_dotenv()` — revisit when wiring Phase 5.
- **Verify SDK behavior against the *installed source* on the *actual machine*, every time.** Alpha SDK churn + machine migration both invalidate prior probe results; the docs contradict the installed code in places. And detect tool *execution* by inspecting `ToolResultBlock` output — never by scanning a message's `repr()` for the command string (the agent's refusal repeats it → false positive).

### Known bugs (tracked in `docs/PROGRESS.md` → WIP)

*(None currently. The `open_application` Chrome silent-lie was fixed and live-verified in the Phase 3 wrap commit `283d44b`, 2026-05-30.)*

### Tooling / dependency lessons

- **Use `ddgs` directly, NOT `langchain-community`.** During Phase-3
  Tool-#4, we discovered `langchain-community` is being sunset (per its
  own deprecation warning) and unbundled its `duckduckgo-search` dep
  (renamed `ddgs`). Going directly to `ddgs` gives us 1 dep instead of
  28, no deprecation, and structured results (`title`, `href`, `body`)
  we format ourselves. **Standing rule:** when a future tool needs a
  capability, prefer the direct library over a meta-package wrapper.
- **Use `pywinctl`, not `pygetwindow`, for Windows window control.**
  Discovered during Phase-3 Tool #5: `pygetwindow` has been stagnant
  since Oct 2020 (Beta status, no updates in 5 years). `pywinctl` is
  the maintained successor by a different author (Sep 2024 release),
  same API surface (`activate` / `minimize` / `close`), cross-platform,
  pulls in `pywin32` for reliable Win32 calls. **Standing rule:** when
  a PROGRESS.md-recommended library is "mature-old", re-check its PyPI
  maintenance status before installing — version churn (or stagnation)
  in the Python ecosystem is constant.

### Periodic research passes (proactive improvement, complements reactive bug-driven learning)
At each major phase boundary (start of Phase 5, start of Phase 6, etc.), the planning chat does a research pass: scan recent open-source Jarvis/agentic-assistant projects, framework releases (Claude Agent SDK, ElevenLabs SDK), OWASP/governance updates, and active research patterns relevant to the upcoming phase. Output: 2-4 concrete proposals (adopt / consider-later / reject) added to the Decision log. Reactive learning (capturing lessons from bugs we hit) continues every session; proactive research happens at phase boundaries only — keep it targeted, not generic. Don't over-do it: quality of proposals > volume.

### Backups & recovery
The repo must be recoverable if Rafael's PC dies or he switches machines. Two layers: (1) PRIMARY — a PRIVATE GitHub remote (version-controlled; clone onto any machine). Once a remote is configured, Claude Code commits AND pushes at the end of every session; CONTEXT.md and PROGRESS.md back up automatically because they live in the repo. (2) SECONDARY — Google Drive for Desktop / OneDrive give passive file-level sync. HARD RULE: .env and secrets are NEVER committed or pushed — .gitignore must exclude .env (a private GitHub remote is safer than raw cloud-folder sync precisely because .gitignore keeps secrets out). Never let one folder be synced by two cloud clients at once (OneDrive + Drive fighting over the same folder causes conflicts). **The private GitHub remote was configured AND the first push landed 2026-05-31** (`origin` → `https://github.com/rafaelxoliver4-art/Jarvis.git`); secret-safety pre-flight passed (`.env` never tracked, never in history, gitignored). GitHub is now the backup of record (no longer OneDrive-only); from here, commit AND push at the end of every session. **Strongly consider cloning OUTSIDE OneDrive** (e.g. `C:\Users\rafae\dev\Jarvis\`) and working from there: OneDrive has now corrupted both the venv AND git internals (`.git/logs/HEAD`) on synced folders, so a clone off the synced path dodges both risks while GitHub remains the backup of record.

**OneDrive-corrupts-git-internals lesson (2026-05-31).** Beyond the venv, OneDrive can also corrupt `.git` internals on a synced folder. Symptom: `git commit` failed with `cannot update the ref 'HEAD': unable to append to '.git/logs/HEAD': Invalid argument`. Repo-local fix that worked: `git config windows.appendAtomically false`. It's the same class of issue as the OneDrive venv corruption — another reason the long-term home should be a clone outside OneDrive.

**Machine-migration lesson (empirical, 2026-05-31 — Rafael switched PCs).** When the Jarvis folder syncs to a new machine via OneDrive, what carries over and what doesn't:
- **Carries over:** all repo files, full git history, `docs/`, and `.env` (OneDrive syncs it as a file even though git ignores it — convenient, but it means secrets ride on the cloud-sync layer, not git).
- **Does NOT carry over: the `venv`.** A virtualenv hard-codes the *creating machine's* absolute interpreter path (and username casing) in `venv/pyvenv.cfg` and its scripts. On a new box those paths are dead. **Always rebuild the venv from scratch on the new machine** (`python -m venv venv` + `pip install -r requirements.txt`) — never trust a synced venv. This is why the pinned `requirements.txt` is the real portable environment, and why a clone-from-GitHub flow is cleaner than dragging a synced folder (it never copies the dead venv in the first place).
- **Also verify the target machine actually has the right Python.** A fresh Windows PC often ships only the Microsoft Store `python.exe` *stub* (prints "Python não foi encontrado", installs nothing) — not a real interpreter. Confirm a real 3.12 is installed (registry `HKLM/HKCU\SOFTWARE\Python`, or `py -0p`, or conda) before rebuilding.

### Capability lives in the brain + hands, NOT the voice layer
The three layers are independent: voice (ElevenLabs — ears/mouth), brain (Claude — decides), hands (`tools.py` + `delegate_task` — act on the machine). What Jarvis can do is set by brain + tool quality, both independent of how speech is handled. Local voice stacks feel "more powerful" but aren't — a local small-model brain is weaker than frontier Claude. Local's real advantages (cost, privacy, offline, latency) are voice-layer properties, and that layer is cleanly swappable. **Standing decision:** keep cloud ElevenLabs + cloud Claude brain through the north-star phases; a local-voice swap (faster-whisper + Ollama + Piper/XTTS + Silero VAD on Windows — NOT MLX, Mac-only) is a FUTURE option driven by cost/privacy, never a capability upgrade, never the brain. **Safety note:** "full machine control" local projects (e.g. Open Interpreter) get raw power by running arbitrary code — exactly the excessive-autonomy / unsafe-code-execution risk our guardrails prevent. For a voice-triggered agent, those guardrails are load-bearing.

### Explicit scope boundaries (what we are NOT building)
These were considered and deliberately rejected during the architecture validation pass. A new session proposing any of these should be pushed back on.

- **NOT runtime self-modification.** The assistant does not edit its own code or tools live. All capability changes go through the supervised Claude Code path Rafael approves. Phase 6.5 ("self-improvement") means procedural memory of past task outcomes, NOT the assistant rewriting itself.
- **NOT multi-agent debate or dynamic tool creation at runtime.** Both attractive in research literature, both premature and complexity-heavy for a single-user personal assistant. Revisit only if a concrete need emerges.
- **NOT open-ended shell access.** Voice + arbitrary shell = remote-code-execution risk. Every system action runs against an allow-list.
- **NOT cloud-stored personal memory.** Memory stays local on Rafael's machine, with schema-validated writes (a defense against memory poisoning — OWASP agentic risk #5).
- **NOT a chatbot.** If a feature is just "answer questions in voice," it doesn't belong here — that's what the agent's brain already does. New tools must take concrete action.
- **NOT unbounded autonomy.** Autonomous background operation (running pre-approved tasks while Rafael is away — e.g. a morning briefing to `./generated/`) is a *future, BOUNDED-only* backlog item (Phase 7+, after 5/6/6.5): it runs ONLY through the existing allow-lists + `./generated/` sandbox + `delegate_task` caps (`max_turns`/timeout/`max_budget_usd`) + `wrap_log` audit, and NEVER performs irreversible or confirmation-gated actions while unattended. Reject any "JARVIS roams free / does whatever it wants overnight" framing — that's the OWASP excessive-autonomy / rogue-agents risk our guardrails exist to prevent.

---

## 4. Doc map — where to look for what

| Need to know... | Read |
|---|---|
| **The "read first" briefing (this file)** | **`CONTEXT.md`** |
| **Current state, next action, recent decisions** | **`docs/PROGRESS.md`** |
| The rules of how Claude Code operates | `CLAUDE.md` |
| The project vision + capability roadmap | `README.md`, `docs/CAPABILITIES.md` |
| The technical architecture in depth | `docs/ARCHITECTURE.md` |
| Phased build prompts to paste into Claude Code | `docs/BUILD_GUIDE.md` |
| Reusable prompts (Jarvis system prompt, debug template) | `docs/PROMPT_LIBRARY.md` |
| The actual code | `tools.py` (capabilities), `tool_logging.py` (telemetry), `main.py` (voice loop wiring) |
| Persistent memory / self-improvement | `memory/` (added Phase 6), `agents/` (added Phase 5) |
| The original kickoff brief (historical) | `JARVIS_KICKOFF.md` |

---

## 5. For Rafael — how to use this file across sessions

Treat `CONTEXT.md` as the **first thing you upload** to any new Claude
conversation about JARVIS:

- **For Claude Code in this repo:** the agent reads it automatically because
  `CLAUDE.md` references it in the session-start ritual.
- **For your planning chat (Claude.ai):** upload alongside `docs/PROGRESS.md`.
  CONTEXT gives the planning chat the durable knowledge of how we work and
  what we've learned; PROGRESS gives it the current state and Next action.
  Together they let any fresh planning-chat conversation hit the ground
  running.
- **For ad-hoc Claude conversations** (e.g. you have a quick question
  outside the main flow): upload CONTEXT.md and the relevant file (a tool
  source, a log file, etc.). Skip PROGRESS.md if it's not state-relevant.

### When to update this file

The natural cadence is: **after a phase wraps + a meaningful learning has
landed.** Not for tiny changes (those go in PROGRESS.md), but for:

- A new foundational rule we discovered (e.g. *"Wait for response" must be
  on for return-valued tools*).
- A bug class with a permanent lesson (e.g. *Windows shell launches don't
  raise on missing exe*).
- A standing convention that future tools should follow.
- An architectural decision that future Claude sessions need to know.

When PROGRESS.md's Decision log gets a new entry that *should outlive the
current phase*, mirror its essence here.

---

## 6. Update history

- **2026-06-01** — **Operating model → three-part team.** Added **JARVIS Research** (separate Claude.ai project) as a researcher sidecar (decision-ready adopt/consider/reject proposals; informs the plan, doesn't hijack the build order) alongside the Planning chat (architect) and Claude Code (builder), with Rafael as bridge. Noted that Claude Code can REQUEST a research pass by flagging open questions as "worth a research pass." Mirrored in CLAUDE.md § Operating model.
- **2026-06-01** — **Bounded-autonomy scope boundary added** to § Explicit scope boundaries: autonomous background operation is a future, BOUNDED-only backlog item (allow-lists + `./generated/` sandbox + `delegate_task` caps + `wrap_log`; never unattended irreversible actions) — reject any unbounded "roams free" framing (OWASP excessive-autonomy). Mirrors the new PROGRESS.md backlog entry. (PROGRESS.md also now carries the proposed Phase 5 v1 design, the resolved `claude-agent-sdk==0.2.87`-pin decision, and a read-only `tools.py`/`main.py` code-state snapshot for the build prompt.)
- **2026-05-31** — **Phase 5 SDK probe re-run on the new machine.** Added a "Claude Agent SDK lessons" block to § 3: bundled CLI needs no system Node; `can_use_tool` is the secondary deny layer (`disallowed_tools` is primary, `PreToolUse` hook for total coverage); `load_dotenv(override=True)` so the real `ANTHROPIC_API_KEY` reaches the SDK subprocess; always verify against installed source on the actual machine. `claude-agent-sdk 0.2.87` now installed in the venv (unpinned until the Phase 5 build commit). Full probe detail in PROGRESS.md.
- **2026-05-31** — **Private GitHub remote configured + first push LANDED + OneDrive-corrupts-git lesson.** Added the backup remote (`origin` → the private `rafaelxoliver4-art/Jarvis` repo) after a clean secret-safety pre-flight; first push (37 commits) confirmed up after Rafael completed GitHub auth. GitHub is now the backup of record. Recorded a new lesson in § Backups & recovery: OneDrive can corrupt `.git` internals (not just the venv) — `git config windows.appendAtomically false` fixed a failed commit — strengthening the case to eventually work from a clone OUTSIDE OneDrive. Detail in PROGRESS.md WIP.
- **2026-05-31** — **Machine migration — env rebuild ✅ DONE.** Rafael switched to a new Windows PC; the Jarvis folder synced down via OneDrive (files + git history + `.env` intact) but the synced `venv` was the old machine's and unusable. Added the "Machine-migration lesson" to § Backups & recovery (a venv hard-codes absolute interpreter paths and never survives a machine switch — rebuild from `requirements.txt`; also verify the new box has a real Python, not just the MS Store stub). Rafael installed **Python 3.12.10**; the venv was rebuilt from scratch and the Phase 1–3 deps re-installed cleanly (PyAudio from the prebuilt cp312 wheel; `import tools` → `ClientTools`; `.env` real + gitignored). `claude-agent-sdk` was deliberately deferred to the Phase 5 probe step (option B) — the venv intentionally lags `requirements.txt` by that one line until then. Full detail + the remaining probe-step `claude-agent-sdk` pin question live in PROGRESS.md.
- **2026-05-30** — Added the Backups & recovery standing rule (private GitHub remote primary + Drive/OneDrive secondary; secrets never pushed). Also retroactively logs today's earlier additions made by an earlier prompt: the "Capability lives in the brain + hands" principle (§3) and the "End goal" line (North star, why JARVIS exists — turn Rafael's ideas into shipped products).
- **2026-05-30** — Added phase-boundary research-pass cadence to standing conventions. Proactive improvement (scan ecosystem at each phase boundary) complements the existing reactive improvement (capture lessons from bugs as they happen).
- **2026-05-30** — **Phase 3 ✅ COMPLETE.** All 5 core tools live-verified. Tool #5 (`control_window`) added three durable lessons baked into § 3: (1) post-action verification on state-mutating OS-wrapper calls (pywinctl silently no-ops when Windows refuses an action); (2) UWP multi-handle picking-largest heuristic (Calculator opens 4 handles); (3) minimize+restore workaround for Windows anti-focus-stealing. `open_application` Chrome silent-lie bug fixed in the same wrap commit (`283d44b`) — registry-aware `cmd /c start "" target` live-verified end-to-end via voice test (Rafael said *"open Chrome"* / *"close Chrome"* — both worked). Known-bugs section now empty. Next: Phase 5 (`delegate_task` via Claude Agent SDK).
- **2026-05-26** — Architectural validation pass — design compared to OpenJarvis / OpenClaw / Microsoft Agent Governance Toolkit / OWASP Top 10 for Agentic Apps 2026; confirmed core decisions match consensus 2026 best practice. Three additions pre-noted for their respective future phases (see PROGRESS.md Decision log).
- **2026-05-26** — Phase 3 Tool #5 (`control_window`) build added three durable Windows-development lessons: prefer `pywinctl` over the stagnant `pygetwindow`; use `cmd /c start "" target` for registry-aware Windows app launching (not bare-exe Popen); use case-insensitive partial title substring matching for locale-friendly window targeting (verified empirically against PT-BR "Calculadora" matching "calc").
- **2026-05-26** — `search_web` empirical timeout data — bumped the `search_web` Response-timeout standing rule from "15s" to "10–15s (verified live with a 2072 ms DDG round-trip)". Plus a new Decision-log entry on the standing pattern: when voice tests are noisy (e.g., audio echo loop), look at code-side evidence (wrap_log, duration_ms, direct-call replay) FIRST before doubting the result.
- **2026-05-26** — Planning-chat additions — phase-reorder rationale, verifiability constraint on Phase 6.5, and an explicit out-of-scope section so future sessions don't re-propose runtime self-modification, multi-agent debate, dynamic tool creation, or cloud-stored memory.
- **2026-05-26** — Created during Phase 3 Tool #4 (`search_web`) build.
  Consolidates conventions and learnings from Phases 0 through Phase 3
  Tool #4. Idea: Rafael wanted a durable "from scratch" briefing that
  works for both Claude Code AND the Claude.ai planning chat, separate
  from PROGRESS.md (which is state-only and updates session-by-session).
