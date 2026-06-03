"""JARVIS persistent local memory (Phase 6).

Explicit-only memory: facts are written ONLY when the user explicitly asks
("remember that X"). No passive extraction, no embeddings, no database — a
local append-only JSON Lines file (`memory/memories.jsonl`) with deterministic
retrieval. Personal memory NEVER leaves the machine (gitignored).

See `memory/store.py` for the storage, validation, recall, and session-start
loader logic.
"""
