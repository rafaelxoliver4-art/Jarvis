"""
JARVIS — tool-usage telemetry (Phase 1.5)

Append-only logging for every client tool, so Phase 6.5's self-improvement loop
has a full history of "what was called, what happened, what failed" to learn
from. Records land in logs/usage_log.jsonl as one JSON object per line.

Design contract (the things this module promises):

  THREAD-SAFE
    The ElevenLabs Conversation runs on a background thread and a tool may be
    invoked while another is still mid-call. A module-level threading.Lock()
    serialises file appends. Sufficient for a single-process app — do not
    upgrade to a queue without a real reason.

  FAIL-OPEN
    If anything inside the logging wrapper raises (disk full, permission
    error, JSON encode failure on a weird value, etc.), the exception is
    SWALLOWED and the underlying tool's result (or exception) is still
    returned/re-raised. Logging must NEVER break or block a real tool action.

  SECRETS-SAFE
    For every param key, if the key name (case-insensitive) contains any of:
      key, token, secret, password, passwd, api, auth, credential
    the value is replaced with "<redacted>" in the log. Non-sensitive values
    are str()-coerced and truncated to MAX_VALUE_LEN chars.

    Known limitation: substring matching is greedy ("monkey" contains "key",
    "rapidapi" contains "api"). Over-redaction is preferred over leakage.
    Redaction is TOP-LEVEL ONLY — nested dicts are not recursed into. Today's
    tools all take flat param dicts, so this is fine. Add recursion when a
    future tool needs nested params.

  NOT LOGGED (deliberate)
    - Tool return values (could contain personal data; outcome flag is enough)
    - Stack traces (just the error type + message)
    - Anything from .env

Usage:
    from tool_logging import wrap_log
    client_tools.register("open_application", wrap_log(open_application))
"""

import json
import os
import threading
from datetime import datetime, timezone

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
LOG_PATH = os.path.join(LOG_DIR, "usage_log.jsonl")

# Truncate non-redacted values at this length (chars). Keeps log lines bounded.
MAX_VALUE_LEN = 80

# Case-insensitive substring match. If a param key contains any of these, the
# value is replaced with "<redacted>" in the log.
_SENSITIVE_KEY_SUBSTRINGS = (
    "key",
    "token",
    "secret",
    "password",
    "passwd",
    "api",
    "auth",
    "credential",
)

# Module-level lock — all wrapped tools share it. Cheap; sufficient for our
# single-process voice loop.
_lock = threading.Lock()


def _truncate(v) -> str:
    """Coerce to str and truncate to MAX_VALUE_LEN chars."""
    s = str(v)
    if len(s) > MAX_VALUE_LEN:
        s = s[:MAX_VALUE_LEN] + "..."
    return s


def _redact_params(params):
    """Return a redaction-safe copy of params for logging.

    Top-level keys only (see module docstring). For non-dict params, returns
    a single-key summary instead of trying to introspect.
    """
    if not isinstance(params, dict):
        return {"_summary": _truncate(repr(params))}

    out = {}
    for k, v in params.items():
        kl = str(k).lower()
        if any(sub in kl for sub in _SENSITIVE_KEY_SUBSTRINGS):
            out[k] = "<redacted>"
        else:
            out[k] = _truncate(v)
    return out


def wrap_log(tool_fn):
    """Wrap a client-tool function with append-only telemetry.

    The returned wrapper preserves the (parameters) -> str contract that the
    ElevenLabs ClientTools registry expects. Logging is best-effort: any
    exception inside the logging path is swallowed (fail-open).

    Tool exceptions: caught, logged with outcome="error", then RE-RAISED
    unchanged so the SDK / agent see the real error.
    """
    tool_name = tool_fn.__name__

    def wrapped(parameters):
        t0 = datetime.now(timezone.utc)
        outcome = "ok"
        error_msg = None
        tool_exc = None
        result = None

        # --- Run the real tool ---
        try:
            result = tool_fn(parameters)
        except Exception as e:  # noqa: BLE001 — we re-raise after logging
            outcome = "error"
            error_msg = f"{type(e).__name__}: {e}"
            tool_exc = e

        t1 = datetime.now(timezone.utc)

        # --- Log it (fail-open) ---
        try:
            record = {
                "ts_start": t0.isoformat(),
                "ts_end": t1.isoformat(),
                "duration_ms": int((t1 - t0).total_seconds() * 1000),
                "tool": tool_name,
                "outcome": outcome,
                "params": _redact_params(parameters),
            }
            if error_msg is not None:
                record["error"] = error_msg

            with _lock:
                os.makedirs(LOG_DIR, exist_ok=True)
                with open(LOG_PATH, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception:  # noqa: BLE001 — fail-open by design
            pass

        # --- Return tool's result or re-raise tool's exception ---
        if tool_exc is not None:
            raise tool_exc
        return result

    # Preserve identity for introspection / debugging
    wrapped.__name__ = tool_name
    wrapped.__doc__ = tool_fn.__doc__
    return wrapped
