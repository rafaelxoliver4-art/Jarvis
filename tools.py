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
import os
import platform
import subprocess
import sys
from datetime import datetime

import psutil
from ddgs import DDGS

from elevenlabs.conversational_ai.conversation import ClientTools

from tool_logging import wrap_log

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
# Phase 1.5: every tool is wrapped with wrap_log() at registration time so
# every call is recorded in logs/usage_log.jsonl from birth. The wrapper is
# thread-safe, fail-open, and secrets-safe — see tool_logging.py for details.
client_tools.register("open_application", wrap_log(open_application))
client_tools.register("save_file",        wrap_log(save_file))
client_tools.register("create_html_file", wrap_log(create_html_file))
client_tools.register("search_web",       wrap_log(search_web))
client_tools.register("get_system_info",  wrap_log(get_system_info))
client_tools.register("delegate_task",    wrap_log(delegate_task))

# Dashboard registration cheat-sheet (add these as Client Tools in ElevenLabs):
#   open_application — "Open a desktop app the user names."   param: app_name (string)
#   save_file        — "Save text to a file."                 params: file_name (string), data (string)
#   create_html_file — "Render a styled HTML page and save."  params: file_name (string, .html), data (string, body), title (string, optional)
#   search_web       — "Search the web (DuckDuckGo)."         param: query (string). REQUIRES Wait-for-response ENABLED + Response timeout 15s.
#   get_system_info  — "Read out current system status."      params: none (the SDK auto-injects tool_call_id)
#   delegate_task    — "Run a complex multi-step task."       param: goal (string)
