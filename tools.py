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
