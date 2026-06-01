"""JARVIS delegated-agent loops (Phase 5).

This package holds the autonomous Claude Agent SDK worker that `delegate_task`
launches as a SEPARATE, killable child process. Nothing here runs inside the
ElevenLabs/voice process — that isolation is the safety spine: a wall-clock
timeout in `tools.delegate_task` can terminate the entire worker process tree
(worker + the SDK's bundled CLI subprocess) even if the SDK loop hangs.
"""
