import os
from dotenv import load_dotenv

# Load and assign environment variables to be imported throughout application

load_dotenv()

# Vonage
VONAGE_APPLICATION_ID = os.getenv("VONAGE_APPLICATION_ID")
VONAGE_PRIVATE_KEY_PATH = os.getenv("VONAGE_PRIVATE_KEY_PATH", "private.key")
VONAGE_VIRTUAL_NUMBER = os.getenv("VONAGE_VIRTUAL_NUMBER")
MAX_CALL_DURATION = int(os.getenv("MAX_CALL_DURATION", "300"))

# Deepgram
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
DEEPGRAM_VOICE_AGENT_ENDPOINT = os.getenv(
    "DEEPGRAM_VOICE_AGENT_ENDPOINT", "agent.deepgram.com/v1/agent/converse"
)
DEEPGRAM_AGENT_SPEAK = os.getenv("DEEPGRAM_AGENT_SPEAK", "aura-orion-en")
