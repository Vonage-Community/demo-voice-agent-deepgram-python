# Voice AI Demo — Vonage + Deepgram

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

## Prerequisites

- Python 3.9+
- [Vonage API account](https://dashboard.nexmo.com) — free tier works
- [Deepgram account](https://console.deepgram.com) — free tier works
- [ngrok](https://ngrok.com) (or any tunnel) to expose localhost

## Project Structure

```
TODO
```

---

## Setup

### 1. Clone and install

```bash
git clone <your-repo-url>
cd voice-ai-demo
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure credentials

```bash
cp .env.template .env
```

Open `.env` and fill in your values:

| Variable | Where to find it |
|---|---|
| `APP_ID` | [Vonage Dashboard → Applications](https://dashboard.nexmo.com/applications) |
| `PRIVATE_KEY_PATH` | Path to `private.key` downloaded when creating your Vonage app |
| `SERVICE_PHONE_NUMBER` | Your Vonage virtual number (E.164, no `+`) |
| `DEEPGRAM_API_KEY` | [Deepgram Console](https://console.deepgram.com) |

### 3. Create a Vonage Application
Use the [Vonage Dashboard](https://dashboard.nexmo.com/applications/new):
1. Create a new application
2. Click **Generate public and private key** — download `private.key`
3. Enable **Voice** capability
4. Set Answer URL and Event URL (update after ngrok step below)
5. Link your Vonage number to the application

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

