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

import html
import json
import os
import platform
import subprocess
import sys
import threading
import time
from datetime import datetime

import psutil
import pywinctl
from ddgs import DDGS

from elevenlabs.conversational_ai.conversation import ClientTools

from tool_logging import wrap_log
from memory.store import recall_facts, remember_fact  # Phase 6 persistent memory

# ---------------------------------------------------------------------------
# Safety helpers
# ---------------------------------------------------------------------------

GENERATED_DIR = os.path.join(os.path.dirname(__file__), "generated")
os.makedirs(GENERATED_DIR, exist_ok=True)


def _safe_path(file_name: str) -> str:
    """Resolve a filename to a path INSIDE ./generated/, refusing escapes.

    Phase 3 Tool #2 (2026-05-25) tightened this to also reject any forward
    slash or backslash in the file_name — even non-escape subpaths like
    "subdir/note.txt". Reasons:
      1. Matches the agent's voice description ("Plain name only — no paths").
      2. Without auto-mkdir of parent dirs, subpaths crash at open() with
         FileNotFoundError instead of being refused politely.
      3. Keeps the safety story consistent: any path-like file_name → refuse.
    The realpath sandbox check below remains as the bedrock fallback in case
    a future os.path implementation lets something through.
    """
    if (not file_name
            or os.path.isabs(file_name)
            or ".." in file_name.replace("\\", "/").split("/")
            or "/" in file_name
            or "\\" in file_name):
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
            # Phase 3 Tool #5 fix (2026-05-26): use `cmd /c start "" target`
            # instead of `Popen(target, shell=True)`. The old form silently
            # failed when `target` wasn't a Windows-PATH builtin (chrome,
            # spotify, vscode) — Popen would launch a shell, the shell couldn't
            # find the exe, but Popen returned without raising so the function
            # claimed success. The `start` command is registry-aware (resolves
            # exes via App Paths) and reliably finds installed apps. The
            # empty "" is the window-title placeholder `start` expects when
            # the first quoted arg is the program path.
            subprocess.Popen(["cmd", "/c", "start", "", target], shell=False)
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


def create_html_file(parameters) -> str:
    """Render a small styled HTML page and save it into ./generated/ only.

    Required params:
      - file_name (str): must end in .html (case-insensitive). Plain name only;
        same sandbox rules as save_file via _safe_path() — no '/', no '\\',
        no '..', no absolute paths.
      - data (str): body text. Newlines become <br> in the rendered page.

    Optional param:
      - title (str): page title. Defaults to "Untitled" if missing or empty.

    Both title and data are HTML-escaped (via html.escape) before being
    written into the template — prevents accidental tag interpretation.
    Returns a short voice-friendly confirmation string.
    """
    file_name = parameters.get("file_name") or "page.html"
    data      = parameters.get("data") or ""
    title     = parameters.get("title") or "Untitled"

    # Extension check (must end in .html, case-insensitive — no auto-append)
    if not file_name.lower().endswith(".html"):
        return "That file needs a .html extension, sir. I can only create HTML pages here."

    # Sandbox check — _safe_path was hardened in Phase 3 Tool #2 to reject any
    # '/' or '\\' as well as '..' / absolute paths.
    try:
        path = _safe_path(file_name)
    except ValueError:
        return "That file location isn't allowed, sir. I can only save inside the generated folder."

    # Escape both title and body to prevent accidental tag interpretation in
    # the saved file. Then turn newlines in the body into <br> so multi-line
    # input renders naturally instead of collapsing.
    safe_title = html.escape(title)
    safe_body  = html.escape(data).replace("\n", "<br>\n")

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{safe_title}</title>
  <style>
    body {{ font-family: system-ui, -apple-system, sans-serif; max-width: 720px;
            margin: 2em auto; padding: 0 1em; line-height: 1.6; color: #222; }}
    h1   {{ border-bottom: 2px solid #444; padding-bottom: 0.3em; }}
  </style>
</head>
<body>
  <h1>{safe_title}</h1>
  <p>{safe_body}</p>
</body>
</html>
"""

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(page)
    return f"Saved {os.path.basename(path)}, sir."


# Cap on the returned summary so Jarvis doesn't read a wall of text aloud.
_SEARCH_MAX_CHARS = 500


def search_web(parameters) -> str:
    """Search DuckDuckGo and return a short text summary (voice-friendly).

    Required param:
      - query (string): the user's search query, in natural language.

    Graceful degradation: any network / library error is caught and the
    function returns a polite refusal string ("I couldn't search just now,
    sir.") rather than raising. The underlying exception is printed to
    stderr as a breadcrumb for debugging (NOT captured in wrap_log, which
    only sees outcome=ok on this path). Consistent with the save_file
    pattern (catch internal errors, return polite string).

    Result is truncated at ~500 chars with "..." so the agent doesn't
    read out a wall of search snippets in voice.

    Phase 3 Tool #4 (2026-05-26). Uses ddgs directly — see Decision log
    re: why we don't use langchain-community's DuckDuckGoSearchRun.
    """
    query = (parameters.get("query") or "").strip()
    if not query:
        return "What would you like me to search for, sir?"

    try:
        results = DDGS().text(query, max_results=3)
    except Exception as exc:  # noqa: BLE001 — graceful degradation by design
        # Breadcrumb to stderr for debugging. NOT to wrap_log; the function
        # itself "succeeded" by returning a polite string (outcome=ok in
        # wrap_log), matching the save_file refusal-on-bad-input pattern.
        print(f"[search_web] {type(exc).__name__}: {exc}", file=sys.stderr)
        return "I couldn't search just now, sir."

    if not results:
        return "I didn't find anything useful for that, sir."

    # Build a compact summary: each result becomes "{title}: {body}".
    # Cap the overall string at _SEARCH_MAX_CHARS so the voice readback
    # stays short.
    pieces = []
    for r in results:
        title = (r.get("title") or "").strip()
        body  = (r.get("body")  or "").strip()
        if title and body:
            pieces.append(f"{title}: {body}")
        elif body:
            pieces.append(body)
        elif title:
            pieces.append(title)

    summary = " — ".join(pieces) if pieces else "I didn't find anything useful for that, sir."

    if len(summary) > _SEARCH_MAX_CHARS:
        summary = summary[:_SEARCH_MAX_CHARS].rstrip() + "..."

    return summary


# Allow-listed actions for control_window. Adding new actions here = adding new
# capability; both action AND app_name must be on-list (structural safety).
_CONTROL_ACTIONS = ("focus", "minimize", "close")

# Allow-listed apps with their window-title patterns. Patterns are matched
# CASE-INSENSITIVE SUBSTRING against w.title.lower(). The substring approach
# is deliberately locale-friendly: "calc" matches both English "Calculator"
# and PT-BR "Calculadora"; non-cognate names (notes vs bloco de notas) get
# multiple alternative patterns. Extend deliberately.
_APP_WINDOW_PATTERNS = {
    "chrome":     ["chrome"],
    "vscode":     ["visual studio code"],
    "calculator": ["calc"],                          # en + pt locales
    "notes":      ["notepad", "bloco de notas"],     # en + pt locales
    "spotify":    ["spotify"],
}


def control_window(parameters) -> str:
    """Focus, minimize, or close an allow-listed app's window.

    Required params:
      - action (str): one of "focus", "minimize", "close" (allow-list).
      - app_name (str): friendly name from the same family as open_application
        (chrome, vscode, calculator, notes, spotify) — allow-listed.

    Refuses politely (returns a string, never raises) on:
      - unknown action / app_name
      - target window not currently open
      - window-system errors at enumeration or action time

    Uses pywinctl (active fork of pygetwindow). Window-title matching is
    case-insensitive substring — handles PT-BR locale ("Calculadora" matches
    "calc"). First matching window wins; pywinctl returns the topmost.
    """
    action = (parameters.get("action") or "").strip().lower()
    app_name = (parameters.get("app_name") or "").strip().lower()

    if action not in _CONTROL_ACTIONS:
        return "I can only focus, minimize, or close windows, sir."

    if app_name not in _APP_WINDOW_PATTERNS:
        allowed = ", ".join(sorted(_APP_WINDOW_PATTERNS))
        return f"I don't manage '{app_name}', sir. I can manage: {allowed}."

    patterns = _APP_WINDOW_PATTERNS[app_name]

    # Enumerate windows (this can fail on unusual Windows configs)
    try:
        all_windows = pywinctl.getAllWindows()
        matches = [w for w in all_windows
                   if w.title and any(p in w.title.lower() for p in patterns)]
    except Exception as exc:  # noqa: BLE001 — graceful degradation
        print(f"[control_window] enum {type(exc).__name__}: {exc}", file=sys.stderr)
        return "I couldn't reach the window system, sir."

    if not matches:
        return f"{app_name.capitalize()} doesn't seem to be open, sir."

    # UWP apps (Calculator, Notepad on Win11, etc.) spawn multiple window
    # handles per logical app: a main visible window + small ghost/auxiliary
    # handles. "First match wins" can pick a ghost. Picking the largest
    # window by area reliably hits the main visible one.
    # (Phase 3 Tool #5 fix 2026-05-30 — discovered when Calculator's 4-handle
    # arrangement caused the original code to act on a 237x39 ghost handle
    # while the 502x810 main window was untouched.)
    def _window_area(w):
        try:
            return w.size.width * w.size.height
        except Exception:  # noqa: BLE001
            return 0

    target = max(matches, key=_window_area)
    try:
        if action == "focus":
            # Phase 3 Tool #5 fix (2026-05-30): pywinctl.activate() silently
            # fails when Windows blocks focus stealing (SetForegroundWindow
            # restriction). The old code claimed success regardless. Now we
            # VERIFY isActive after; if not, try the minimize+restore
            # workaround which often defeats the focus-stealing block; if
            # THAT also fails, return a polite refusal that's honest about
            # the OS limitation.
            target.activate()
            time.sleep(0.10)  # let Windows process the state change
            if target.isActive:
                return f"{app_name.capitalize()} focused, sir."
            # Workaround: minimize then restore forces a state transition
            # that Windows usually allows even when SetForegroundWindow is
            # refused.
            try:
                target.minimize()
                time.sleep(0.10)
                target.restore()
                time.sleep(0.10)
                if target.isActive:
                    return f"{app_name.capitalize()} focused, sir."
            except Exception:  # noqa: BLE001
                pass  # fall through to polite refusal
            return (f"I couldn't bring {app_name} forward, sir — "
                    f"Windows blocked the focus change.")

        if action == "minimize":
            target.minimize()
            time.sleep(0.10)  # let Windows process
            if target.isMinimized:
                return f"Minimized {app_name}, sir."
            return f"I couldn't minimize {app_name}, sir."

        if action == "close":
            target.close()
            time.sleep(0.20)  # close is slower than min/focus; app may prompt
            # Verify by re-enumerating: is any window matching our patterns
            # still around? (target.isAlive may be stale after close.)
            still_open = [w for w in pywinctl.getAllWindows()
                          if w.title and any(p in w.title.lower() for p in patterns)]
            if not still_open:
                return f"Closed {app_name}, sir."
            return (f"I sent the close request to {app_name}, sir, "
                    f"but its window is still open — it may be prompting "
                    f"you to save.")
    except Exception as exc:  # noqa: BLE001 — graceful degradation
        print(f"[control_window] {action} {type(exc).__name__}: {exc}", file=sys.stderr)
        return f"I couldn't {action} {app_name}, sir."

    return f"I'm not sure what happened with {app_name}, sir."  # belt-and-suspenders


def get_system_info(parameters) -> str:
    """Voice-friendly snapshot of system status (read-only).

    Ignores its parameters — there's no user input for this tool. Returns ONE
    short string suitable for TTS, summarising:
      - Current local time + weekday (12-hour format, cross-platform).
      - Battery percentage + plugged/unplugged (omitted on desktops with no battery).
      - CPU usage % (sampled over 0.5s for accuracy — calling cpu_percent with
        interval=0 returns a meaningless 0.0 on the first call).
      - Memory (RAM) usage %.

    All values are rounded to integers for voice friendliness.
    """
    now = datetime.now()
    # Manual 12-hour conversion (avoids strftime("%-I") which is Linux-only —
    # Windows would need "%#I", so we sidestep the difference entirely):
    hour_12 = now.hour % 12 or 12
    ampm = "AM" if now.hour < 12 else "PM"
    time_str = f"{hour_12}:{now.minute:02d} {ampm} on {now.strftime('%A')}"

    # CPU: blocks 0.5s — needed for an accurate reading on first call.
    cpu_pct = int(round(psutil.cpu_percent(interval=0.5)))
    mem_pct = int(round(psutil.virtual_memory().percent))

    # Battery: sensors_battery() returns None on machines without a battery
    # (e.g., desktops). Omit the clause cleanly in that case.
    battery = psutil.sensors_battery()
    if battery is not None:
        bat_pct = int(round(battery.percent))
        bat_state = "charging" if battery.power_plugged else "on battery"
        bat_clause = f" Battery's at {bat_pct}% and {bat_state}."
    else:
        bat_clause = ""

    return f"It's {time_str}.{bat_clause} CPU's at {cpu_pct}%, memory at {mem_pct}%, sir."


# ---------------------------------------------------------------------------
# Phase 6 — persistent local memory (explicit-only). Thin wrappers over
# memory.store; the real logic (schema, validation, ranking, session loader)
# lives in memory/store.py. These are NOT exposed to the delegate_task worker.
# ---------------------------------------------------------------------------

def remember(parameters) -> str:
    """Store a plain fact the user explicitly asked to remember.

    Required param: content (the fact, in the user's words).
    Optional param: tags (list or comma-separated string) for retrieval.

    Validates + appends to the local memory store. Rejects secrets/credentials
    and any instruction-/policy-change-like content with a polite refusal.
    Returns a short voice-friendly confirmation. EXPLICIT-ONLY: only call this
    when the user actually says "remember ...".
    """
    return remember_fact(parameters.get("content"), parameters.get("tags"))


def recall(parameters) -> str:
    """Recall stored facts relevant to a query (deterministic, top few).

    Required param: query. Returns a short bounded voice string, or a polite
    "nothing stored about that" when there's no match.
    """
    return recall_facts(parameters.get("query"))


# --- delegate_task: launch the SDK loop in a KILLABLE worker process ---------
# Phase 5 Stage 1 (the safety spine). The autonomous Claude Agent SDK loop runs
# in a SEPARATE child process (agents/delegate_worker.py), NOT in this voice
# process. That isolation is what makes the wall-clock timeout a real kill
# switch: on timeout/crash we terminate the entire worker process tree (worker +
# the SDK's bundled CLI subprocess) with psutil, so a hung SDK loop can't run on
# for hours. The goal goes to the worker via STDIN JSON (never argv); the API
# key flows via the inherited environment only.

# Nesting invariant: real delegation completion (~90–94s, measured in voice-test #4)
#   < _WORKER_TIMEOUT_SEC (110s — the parent's HARD wall-clock kill on the worker tree)
#   < ElevenLabs dashboard "Response timeout" (120s — the ElevenLabs MAX; Rafael set it).
# Why 110 not 115/120: on the TIMEOUT path the parent runs the full window AND then
# spends ~3–5s tearing down the worker process tree before it returns, so its
# worst-case return is ~110+5 ≈ 115s — safely under the dashboard's hard 120s cap.
# The SDK inner guards (max_turns=5, max_budget_usd=0.50, API_TIMEOUT_MS,
# CLAUDE_CODE_MAX_RETRIES) are UNCHANGED — they still bound the worker; this only
# gives the wall-clock kill enough room for a healthy run (~94s) to finish.
_WORKER_TIMEOUT_SEC = 110    # HARD wall-clock cap for a delegated task
_DELEGATE_SUMMARY_MAX = 300  # cap the voice readback length

# Concurrency guard: only ONE delegation runs at a time. The ElevenLabs SDK calls
# tools synchronously, so a non-blocking lock is enough; it stops the echo loop /
# impatient repeats from stacking concurrent workers and burning budget.
_delegate_lock = threading.Lock()


def _log_delegation(record: dict) -> None:
    """Best-effort, fail-open, secrets-safe telemetry line for a delegation.

    Writes ONE compact JSON line to logs/delegate_log.jsonl. Logs only metadata
    (truncated goal, tool-call names+outcomes, counts, duration, cost, status) —
    never raw tool outputs, never the voice summary, never .env/keys. Any error
    here is swallowed so telemetry can NEVER break the result or the timeout.
    """
    try:
        log_dir = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, "delegate_log.jsonl"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
    except Exception:  # noqa: BLE001 — telemetry is never load-bearing
        pass


def _kill_process_tree(pid: int) -> None:
    """Terminate a worker process AND all descendants (incl. the SDK CLI)."""
    try:
        parent = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return
    procs = parent.children(recursive=True)
    procs.append(parent)
    for p in procs:
        try:
            p.terminate()
        except psutil.NoSuchProcess:
            pass
    gone, alive = psutil.wait_procs(procs, timeout=3)
    for p in alive:
        try:
            p.kill()
        except psutil.NoSuchProcess:
            pass


def delegate_task(parameters) -> str:
    """Hand a complex, multi-step goal to an autonomous Claude Agent SDK loop.

    SYNCHRONOUS by contract (the ElevenLabs SDK calls tools synchronously). It
    runs the async SDK loop inside a child worker process and waits with a hard
    timeout. Returns a SHORT voice-friendly summary — never the raw result.

    Concurrency-guarded: only one delegation runs at a time. A second call while
    one is in flight returns a short "busy" string instead of spawning another
    worker (prevents the echo loop / impatient repeats from stacking workers and
    burning budget). The flag is released in a finally so a crash can't stick it
    "busy" forever.
    """
    goal = (parameters.get("goal") or "").strip()
    if not goal:
        return "What would you like me to take on, sir?"

    if not _delegate_lock.acquire(blocking=False):
        return "I'm still working on the previous task, sir — one moment."
    try:
        return _run_delegation(goal)
    finally:
        _delegate_lock.release()  # always release, even on crash → never stuck "busy"


def _run_delegation(goal: str) -> str:
    """Spawn the worker process, enforce the hard wall-clock timeout, and return a
    short voice string. (Body unchanged from the original delegate_task — the
    safety spine, process-tree kill, circuit breakers, and telemetry are intact.)
    """
    repo_root = os.path.dirname(os.path.abspath(__file__))
    cmd = [sys.executable, "-m", "agents.delegate_worker"]
    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=repo_root,
            env=os.environ.copy(),  # inherits ANTHROPIC_API_KEY (env-only)
            text=True,
            encoding="utf-8",
        )
    except Exception as exc:  # noqa: BLE001
        print(f"[delegate_task] launch {type(exc).__name__}: {exc}", file=sys.stderr)
        return "I couldn't start the task engine, sir."

    payload = json.dumps({"goal": goal})
    goal_trunc = goal[:80]
    ts = datetime.now().isoformat(timespec="seconds")
    try:
        out, err = proc.communicate(input=payload, timeout=_WORKER_TIMEOUT_SEC)
    except subprocess.TimeoutExpired:
        _kill_process_tree(proc.pid)
        try:
            proc.communicate(timeout=5)
        except Exception:  # noqa: BLE001
            pass
        _log_delegation({"ts": ts, "goal": goal_trunc, "status": "timeout",
                         "duration_ms": _WORKER_TIMEOUT_SEC * 1000})
        return "That task took too long, sir, so I stopped it. Try narrowing it down."
    except Exception as exc:  # noqa: BLE001
        _kill_process_tree(proc.pid)
        print(f"[delegate_task] run {type(exc).__name__}: {exc}", file=sys.stderr)
        _log_delegation({"ts": ts, "goal": goal_trunc, "status": "error"})
        return "Something went wrong while running that task, sir."

    if proc.returncode != 0 or not out:
        print(f"[delegate_task] worker rc={proc.returncode} "
              f"stderr={(err or '')[:200]}", file=sys.stderr)
        _log_delegation({"ts": ts, "goal": goal_trunc, "status": "error",
                         "rc": proc.returncode})
        return "I couldn't complete that task, sir."

    try:
        result = json.loads(out.strip().splitlines()[-1])
    except Exception as exc:  # noqa: BLE001
        print(f"[delegate_task] parse {type(exc).__name__}: {exc}", file=sys.stderr)
        _log_delegation({"ts": ts, "goal": goal_trunc, "status": "error",
                         "note": "unparseable worker output"})
        return "I finished the task, sir, but couldn't read the result cleanly."

    status = result.get("status") or "unknown"
    summary = (result.get("summary") or "").strip()

    # Compact telemetry: metadata only (NO raw outputs, NO summary, NO secrets).
    _log_delegation({
        "ts": ts,
        "goal": goal_trunc,
        "status": status,
        "turns": result.get("turns"),
        "total_tool_calls": result.get("total_tool_calls"),
        "tool_calls": result.get("tool_calls"),
        "duration_ms": result.get("duration_ms"),
        "estimated_cost_usd": result.get("estimated_cost_usd"),
        "stop_reason": result.get("stop_reason"),
        "session_id": result.get("session_id"),
    })

    # Voice readback: short summary, or a status-appropriate fallback.
    if summary:
        return summary[:_DELEGATE_SUMMARY_MAX]
    if status == "success":
        return "I finished, sir, but there was nothing to report."
    if status == "blocked":
        return "I had to stop that task early, sir, to stay within safe limits."
    if status in ("max_turns", "max_budget"):
        return "I reached my limit on that task, sir, and stopped."
    return "I couldn't fully complete that task, sir."


# ---------------------------------------------------------------------------
# Registry  (the agent calls tools by these registered names)
# ---------------------------------------------------------------------------

client_tools = ClientTools()
# Phase 1.5: every tool is wrapped with wrap_log() at registration time so
# every call is recorded in logs/usage_log.jsonl from birth. The wrapper is
# thread-safe, fail-open, and secrets-safe — see tool_logging.py for details.
client_tools.register("open_application", wrap_log(open_application))
client_tools.register("save_file",        wrap_log(save_file))
client_tools.register("create_html_file", wrap_log(create_html_file))
client_tools.register("search_web",       wrap_log(search_web))
client_tools.register("control_window",   wrap_log(control_window))
client_tools.register("get_system_info",  wrap_log(get_system_info))
client_tools.register("delegate_task",    wrap_log(delegate_task))
client_tools.register("remember",         wrap_log(remember))        # Phase 6
client_tools.register("recall",           wrap_log(recall))          # Phase 6

# Dashboard registration cheat-sheet (add these as Client Tools in ElevenLabs):
#   open_application — "Open a desktop app the user names."   param: app_name (string)
#   save_file        — "Save text to a file."                 params: file_name (string), data (string)
#   create_html_file — "Render a styled HTML page and save."  params: file_name (string, .html), data (string, body), title (string, optional)
#   search_web       — "Search the web (DuckDuckGo)."         param: query (string). REQUIRES Wait-for-response ENABLED + Response timeout 15s.
#   control_window   — "Focus / minimize / close a window."   params: action (string: focus|minimize|close), app_name (string). Wait-for-response ENABLED + Response timeout 5s.
#   get_system_info  — "Read out current system status."      params: none (the SDK auto-injects tool_call_id)
#   delegate_task    — "Run a complex multi-step task."       param: goal (string)
#   remember         — "Store a fact the user asks to remember." params: content (string), tags (string, optional). Wait-for-response ENABLED, Response timeout 5s.
#   recall           — "Recall stored facts about a query."   param: query (string). Wait-for-response ENABLED, Response timeout 5s.
