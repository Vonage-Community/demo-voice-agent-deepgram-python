from agent_config import DG_AGENT_SETTINGS
from call_state import CallState
from deepgram_handlers import handle_deepgram
from vonage_handlers import handle_vonage, build_ncco, VONAGE_VOICE
from fastapi.responses import JSONResponse
import logging
from fastapi import FastAPI, Query, Request, WebSocket, WebSocketDisconnect
import websockets
from config import DEEPGRAM_VOICE_AGENT_ENDPOINT, DEEPGRAM_API_KEY
import asyncio
import json

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Webhook: Answer inbound PSTN call
@app.get("/answer")
async def answer(
    request: Request,
    uuid: str = Query(None),
    from_: str = Query(None, alias="from"),
):
    """
    Vonage calls this when a call is answered
    Returns an NCCO that plays a greeting, then connects audio
    to our /socket WebSocket endpoint
    """
    host = request.headers.get("host", request.url.hostname)

    ncco = build_ncco(host=host, uuid=uuid, from_=from_)

    return JSONResponse(content=ncco)


# Webhook: Call status events
@app.post("/event")
async def event(request: Request):
    body = await request.json()
    logger.info(
        f"Call event: {body.get('status', 'unknown')} | UUID: {body.get('uuid')}"
    )
    return JSONResponse(content={"status": "ok"})


# WebSocket: Bridge Vonage <-> Deepgram
@app.websocket("/socket")
async def socket(vonage_ws: WebSocket, original_uuid: str = Query(None)):
    """
    This is the core of the demo. Two WebSocket connections run concurrently:
      - vonage_ws  : the connection Vonage opened to us (caller's audio in,
                     agent audio out)
      - dg_ws      : the connection we open to Deepgram (caller audio in,
                     agent audio + transcripts out)

Two async loops run in parallel via asyncio.gather():
  handle_vonage()   — reads from Vonage, forwards binary audio to Deepgram
  handle_deepgram() — reads from Deepgram, forwards binary audio to Vonage
                      and handles barge-in + transcript logging

Barge-in flow:
  Deepgram detects the caller speaking mid-response
    → fires {"type": "UserStartedSpeaking"}
    → we send {"action": "clear"} to Vonage
    → Vonage discards its audio buffer instantly
    → caller's new speech takes over
"""
    await vonage_ws.accept()
    logger.info(f"Vonage WS connected | UUID: {original_uuid}")

    state = CallState()
    
    try:
        dg_uri     = f"wss://{DEEPGRAM_VOICE_AGENT_ENDPOINT}"
        dg_headers = {"Authorization": f"token {DEEPGRAM_API_KEY}"}

        logger.info("Connecting to Deepgram Voice Agent...")

        async with websockets.connect(dg_uri, additional_headers=dg_headers) as dg_ws:

            # Send the agent configuration as the very first message.
            # Deepgram will not process audio until it receives this.
            await dg_ws.send(json.dumps(DG_AGENT_SETTINGS))
            state.dg_ws_open = True
            logger.info("Deepgram WS open and configured.")

     
            await asyncio.gather(
                handle_deepgram(dg_ws, vonage_ws, original_uuid, state),
                handle_vonage(vonage_ws, dg_ws, state),
            )


    except Exception as exc:
        logger.error(f"WS bridge error: {exc}")
    finally:
        state.dg_ws_open = False
        logger.info(f"WS session ended | UUID: {original_uuid}")