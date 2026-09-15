import os
from dotenv import load_dotenv

# Environment variables
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


# Logging colors
# Used for color coding logs for demonstration purposes
class LogColor:
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    GREY = "\033[37m"
    RESET = "\033[0m"

    @classmethod
    def wrap(cls, color: str, msg: str) -> str:
        return f"{color}{msg}{cls.RESET}"
