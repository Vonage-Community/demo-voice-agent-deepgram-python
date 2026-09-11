import vonage
import json
from vonage import Vonage, Auth
from vonage_voice import (
    CreateCallRequest,
    Phone,
    ToPhone,
    NccoAction,
    Talk,
    Connect,
    WebsocketEndpoint,
    TtsStreamOptions,
)
from fastapi.responses import JSONResponse
from fastapi import WebSocket, WebSocketDisconnect
import logging
from config import VONAGE_APPLICATION_ID, VONAGE_PRIVATE_KEY_PATH
from call_state import CallState

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

vonage_client = Vonage(
    Auth(
        application_id=VONAGE_APPLICATION_ID,
        private_key=VONAGE_PRIVATE_KEY_PATH,
    )
)
VONAGE_VOICE = vonage_client.voice


def build_ncco(host: str, uuid: str, from_: str) -> list:
    """
    Build and return the NCCO (Call Control Object) for an answered call

    The NCCO does two things:
    1. talk    — plays a brief text-to-speech greeting while the WebSocket connects
    2. connect — tells Vonage to stream the call's audio to /socket over
                WebSocket

    The `uuid` is appended as a query param to the WebSocket URI so that
    the /socket handler knows which call it is serving
    """
    ws_uri = f"wss://{host}/socket?original_uuid={uuid}"

    greeting = "Hello, please wait while we connect your call!"

    websocket_endpoint = WebsocketEndpoint(
        uri=ws_uri, contentType="audio/l16;rate=8000"
    )
    ncco: list[NccoAction] = [
        Talk(text=greeting, language="en-US", style=11),
        Connect(endpoint=[websocket_endpoint], from_=from_),
    ]

    logger.info(f"Inbound call answered. UUID: {uuid}. WebSocket URI: {ws_uri}")
    return [action.model_dump(by_alias=True, exclude_none=True) for action in ncco]


async def handle_vonage(vonage_ws: WebSocket, dg_ws, state: CallState,) -> None:
    """
    Loop 2: Vonage → Deepgram

    Receives messages from Vonage and reacts:
    - bytes              → forward raw PCM caller audio to Deepgram
                            (stopped once ending_call is set, to prevent
                            Deepgram from generating another LLM turn
                            during the hangup window)
    - websocket:connected → log confirmation that the WS leg is ready
    - websocket:cleared   → log confirmation that barge-in buffer was cleared
    """
    try:
        while True:
            message = await vonage_ws.receive()

            if "text" in message:
                # Control event from Vonage (not audio)
                evt = json.loads(message["text"])
                kind = evt.get("event", "")
                logger.info(f"Vonage event: {kind}")

                if kind == "websocket:connected":
                    logger.info(
                        f"Vonage WS ready | " f"content-type: {evt.get('content-type')}"
                    )
                elif kind == "websocket:cleared":
                    logger.info("Vonage buffer cleared (barge-in confirmed)")

            elif "bytes" in message:
                # Raw PCM audio from the caller — forward to Deepgram.
                # Once ending_call is set, stop sending caller audio so
                # Deepgram can't trigger another LLM turn during the
                # sleep window before hangup.
                if state.dg_ws_open and not state.ending_call:
                    await dg_ws.send(message["bytes"])

    except WebSocketDisconnect:
        logger.info("Vonage WS disconnected.")
