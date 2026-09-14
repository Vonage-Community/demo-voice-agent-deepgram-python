# Voice AI Demo With Vonage + Deepgram

A Python server that bridges inbound and outbound PSTN calls to Deepgram's Voice Agent platform for real-time AI conversation with live transcription and barge-in support.

## How It Works

```
Caller dials Vonage number
    → Vonage fetches NCCO from /answer
    → NCCO connects call audio to /socket (WebSocket)
    → server.py opens second WebSocket to Deepgram
    → Caller audio (PCM 8kHz) streams Vonage → Deepgram
    → Deepgram transcribes, reasons, synthesizes speech
    → Agent audio streams Deepgram → Vonage → caller's phone
    → Transcripts log to terminal in real time
    → Caller interrupts → UserStartedSpeaking → CLEAR → barge-in
```
The demo agent is prompted with **Pugsley**, a pug expert who answers questions about pugs, helps callers decide if a pug is right for them, and looks up local pug rescue organizations by zip code using function calling.

### The endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/answer` | Vonage answer webhook, returns a NCCO |
| `POST` | `/event` | Vonage call status events |
| `WS` | `/socket` | Bidirectional audio bridge (Vonage ↔ Deepgram) |

### The architecture

The server maintains two concurrent WebSocket connections per call, managed by a `CallState` dataclass that tracks shared state:

```
CallState (per call)
    ↓
asyncio.gather(
    handle_deepgram()  ← Deepgram → Vonage: audio, transcripts, barge-in, function calls
    handle_vonage()    ← Vonage → Deepgram: caller audio forwarding
)
```

Function calls from the LLM are handled client-side in `dispatch_function_call()`. The `end_call` function is deferred —- its `FunctionCallResponse` is sent only after `AgentAudioDone` fires, ensuring the farewell TTS plays fully before the call is terminated.

### Project structure

```
.
├── server.py            # FastAPI app — routes and WebSocket orchestration
├── agent_config.py      # Deepgram Voice Agent settings (prompt, LLM, TTS, functions)
├── call_state.py        # CallState dataclass — shared mutable state per call
├── deepgram_handlers.py # handle_deepgram(), dispatch_function_call(), find_pug_rescues()
├── vonage_handlers.py   # handle_vonage(), build_ncco(), Vonage client
├── dog_rescue_data.py   # Hardcoded pug rescue lookup data by US zip prefix
├── config.py            # Environment variable loading
├── requirements.txt     # Python dependencies
├── .env.template        # Credential template
└── .gitignore
```

## Get This Code Running

### Prerequisites

- Python 3.9+
- [Vonage API account](https://vonage.dev/4AhETic)
- [Deepgram account](https://console.deepgram.com/signup)
- [ngrok](https://vonage.dev/4d9waov)


### 1. Set up your environment

Set up your environment by cloning the repo, creating and activating a virtual environment, and installing dependencies

```bash
git clone https://github.com/Vonage-Community/demo-voice-agent-deepgram-python.git
cd demo-voice-agent-deepgram-python
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Create a Vonage Application

1. Go to [Vonage Dashboard → Applications](https://vonage.dev/4xrc8Nd)
2. Create a new application and enable **Voice** capability
3. Click **Generate public and private key** to initiate a download of a file called `private.key`; once downloaded, move it to the project root
4. Set placeholder webhook URLs for now (you'll update them after starting ngrok)
5. Link a Voice capable Vonage number to the application

### 3. Configure credentials

```bash
cp .env.template .env
```

Open `.env` and fill in your values:

| Variable | Where to find it |
|---|---|
| `VONAGE_APPLICATION_ID` | [Vonage Dashboard → Applications](https://vonage.dev/4xrc8Nd) |
| `VONAGE_PRIVATE_KEY_PATH` | Path to `private.key` downloaded when creating your Vonage app |
| `VONAGE_VIRTUAL_NUMBER` | Your Vonage virtual number (E.164, no `+`) |
| `DEEPGRAM_API_KEY` | [Deepgram Console](https://console.deepgram.com) |
| `DEEPGRAM_VOICE_AGENT_ENDPOINT` | `agent.deepgram.com/v1/agent/converse` |
| `DEEPGRAM_AGENT_SPEAK` | TTS voice |


### 4. Start ngrok

```bash
ngrok http 3000
```

Copy the `https://` forwarding URL (e.g. `https://abc123.ngrok.io`).

Update your Vonage application webhooks:
- **Answer URL:** `https://abc123.ngrok.io/answer` (GET)
- **Event URL:** `https://abc123.ngrok.io/event` (POST)

### 5. Run the server

```bash
uvicorn server:app --host 0.0.0.0 --port 3000 --reload
```

## Try It Out!

Call your Vonage number from any phone. The voice agent prompted with "Puglsey" will answer and you can:

- Ask anything about pugs
- Ask about adopting a pug, causing the agent to prompt you for your zip code and look up local pug rescues
- When your response indicates you are done with the call (ie, "No, I don't need anything else"), the agent will evaluate the call as complete and respond with an LLM-generated farewell

Watch the terminal for live transcripts:

```
INFO  Deepgram -> {"type": "ConversationText", "role": "user", "content": "should i get a pug?"}
INFO  Deepgram -> {"type": "ConversationText", "role": "assistant", "content": "Pugs are wonderful companions..."}
```

## Resources and References

- [Vonage Applications](https://vonage.dev/4xrc8Nd): Documentation for creating and configuring a Vonage application, including authentication key generation, capability setup, and webhook configuration
- [Vonage Voice API for Developers](https://vonage.dev/4hVQMDB): Overview of the Vonage Voice API including guides for AI voice agents, WebSockets, IVRs, text-to-speech, and speech-to-text
- [Vonage NCCO Reference](https://vonage.dev/4gSorgr): Complete API reference for Nexmo Call Control Objects (NCCOs), including the `connect`, `talk`, `record`, and `input` actions used to control call flow
- [A Comprehensive Guide on Working with Python Virtual Environments](https://vonage.dev/42D6eeT): A guide to creating and managing Python virtual environments using `venv` and `virtualenv`, including dependency management with `requirements.txt`
- [What Are WebSockets and How Are They Different From HTTP?](https://vonage.dev/493ONaY): An explainer on the WebSocket protocol, how it differs from HTTP, and how Vonage uses WebSocket connections in the Voice API for real-time audio streaming
- [AI Voice Agent with Deepgram | Vonage API Documentation](https://developer.vonage.com/en/voice/voice-api/guides/voice-ai-agent-deepgram): Step-by-step guide for building a real-time AI voice agent using the Vonage Voice API and Deepgram's Voice Agent platform, with support for barge-in and live transcription
- [WebSocket Voice Chat API Guide | Vonage API Documentation](https://developer.vonage.com/en/voice/voice-api/concepts/websockets): Conceptual guide to WebSockets in the Vonage Voice API, including binary vs. JSON message parsing, audio streaming patterns, and connecting to AI engines
- [Add Tools and Human Transfer to a Vonage + Deepgram Voice Agent](https://developer.vonage.com/en/blog/add-tools-human-transfer-vonage-deepgram-voice-agent): Tutorial extending a basic Vonage + Deepgram voice agent with function calling, timeouts, fallback handling, human call transfer, and call records
- [Deepgram Voice Agent API — Getting Started](https://developers.deepgram.com/docs/voice-agent): Official Deepgram documentation for building real-time interactive voice agents over a single WebSocket connection, covering STT, LLM integration, TTS, and function calling
- [Deepgram Voice Agent API — Configure the Voice Agent](https://developers.deepgram.com/docs/configure-voice-agent): Full reference for the `Settings` message sent on WebSocket open, including audio format, ASR model, LLM provider, TTS voice, greeting, and function definitions
- [Deepgram Voice Agent API — LLM Models](https://developers.deepgram.com/docs/voice-agent-llm-models): Reference for supported LLM providers and models available through Deepgram's managed service, including Anthropic, OpenAI, Google, and Groq
