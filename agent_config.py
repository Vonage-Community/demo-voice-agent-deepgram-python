# Deepgram Voice Agent Settings

# Sent once on WebSocket open to configure ASR, LLM, and TTS.
# Swap "anthropic" for "open_ai" or "google" — one key change.

DG_AGENT_SETTINGS = {
    "type": "Settings",
    "audio": {
        "input":  {"encoding": "linear16", "sample_rate": 8000},
        "output": {"encoding": "linear16", "sample_rate": 8000, "container": "none"},
    },
    "agent": {
        "listen": {
            "provider": {"type": "deepgram", 
                         "model": "flux-general-en",
                         "version": "v2"},
        },
        "think": {
            "provider": {
                "type":  "anthropic",
                "model": "claude-sonnet-5",
            },
            "prompt": (
                "You are Pugsley, a friendly and enthusiastic pug expert on a live phone call. "
                "You know everything about pugs — their temperament, health needs, grooming, "
                "diet, training, and what it's like to live with one. "
                "You genuinely love pugs and want to help callers make a great decision. "
                "Keep responses concise and natural for spoken conversation — no bullet points, "
                "no lists, no markdown, no asterisks, no special formatting of any kind. "
                "Plain spoken sentences only. "
                "If the caller wants to find local pug rescues or adoptable pugs near them, "
                "ask for their zip code and then call the find_pug_rescues function. "
                "After every response — whether you answered a question, shared rescue results, "
                "or helped with anything else — always end with: "
                "'Is there anything else I can help you with?' "
                "IMPORTANT: When the caller responds to 'Is there anything else I can help you with?' "
                "with ANY negative or closing response — including 'no', 'nope', 'nah', "
                "'that's all', 'I'm good', 'thanks', 'goodbye', 'bye', 'no thank you', "
                "'I'm all set', or any similar closing — follow these steps IN ORDER: "
                "STEP 1: Say exactly one short farewell sentence out loud, such as "
                "'It was great chatting with you, take care!' or 'Happy to help, goodbye!' "
                "STEP 2: Call end_call. "
                "Do NOT skip step 1. Do NOT say more than one sentence. Do NOT call end_call before speaking."
            ),
            "functions": [
                {
                    "name": "find_pug_rescues",
                    "description": (
                        "Find adoptable pugs and pug rescue organizations near the caller. "
                        "Call this when the caller wants to adopt a pug or find local rescues. "
                        "Requires a zip code from the caller."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "zip_code": {
                                "type": "string",
                                "description": "The caller's zip code to search near.",
                            }
                        },
                        "required": ["zip_code"],
                    },
                },
                {
                    "name": "end_call",
                    "description": (
                        "End the phone call. Call this when the caller has no "
                        "more questions or explicitly wants to hang up."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reason": {
                                "type": "string",
                                "description": "Brief reason for ending the call.",
                            }
                        },
                        "required": [],
                    },
                },
            ],
        },
        "speak": {
            "provider": {"type": "deepgram",
                         "model": "flux-kit-en",
                         "version": "v2"},
        },
        "greeting": "Hello! I'm Pugsley, your pug expert. Whether you're thinking about adopting a pug or just want to learn more about them, I'm here to help. What's on your mind?",
    },
}