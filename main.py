"""
JARVIS — main voice loop (STARTER SKELETON)

This file only WIRES UP the conversation: audio, callbacks, and the client-tool registry.
All actual capabilities live in tools.py. Keep business logic OUT of this file.

Run:  python main.py   (after activating the venv and filling in .env)
Stop: Ctrl+C

If the SDK API has changed, fetch the current docs:
  https://elevenlabs.io/docs/eleven-agents/libraries/python
"""

import os
import signal

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

# Our local capabilities (the "hands"). Defined and registered in tools.py.
from tools import client_tools

load_dotenv()

AGENT_ID = os.getenv("AGENT_ID")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")


def main() -> None:
    if not AGENT_ID:
        raise SystemExit("Missing AGENT_ID in .env (copy it from your ElevenLabs agent).")

    elevenlabs = ElevenLabs(api_key=ELEVENLABS_API_KEY)

    conversation = Conversation(
        elevenlabs,
        AGENT_ID,
        # Auth is needed only for private agents (i.e. when an API key is set).
        requires_auth=bool(ELEVENLABS_API_KEY),
        audio_interface=DefaultAudioInterface(),
        # Our local tools the agent can call:
        client_tools=client_tools,
        # Console callbacks so we can see what's happening:
        callback_agent_response=lambda r: print(f"JARVIS: {r}"),
        callback_agent_response_correction=lambda o, c: print(f"JARVIS (corrected): {o} -> {c}"),
        callback_user_transcript=lambda t: print(f"You: {t}"),
    )

    # Clean shutdown on Ctrl+C.
    signal.signal(signal.SIGINT, lambda sig, frame: conversation.end_session())

    print("JARVIS is listening. Speak now. Press Ctrl+C to stop.\n")
    conversation.start_session()

    conversation_id = conversation.wait_for_session_end()
    print(f"\nConversation ended. ID: {conversation_id}")


if __name__ == "__main__":
    main()
