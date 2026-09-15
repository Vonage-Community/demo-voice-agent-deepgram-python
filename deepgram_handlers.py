import asyncio
import json
import logging
from vonage import Vonage, Auth
import websockets
from fastapi import WebSocket
from config import VONAGE_APPLICATION_ID, VONAGE_PRIVATE_KEY_PATH, LogColor
from call_state import CallState
from dog_rescue_data import PUG_RESCUES_BY_REGION, DEFAULT_RESCUES

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


async def find_pug_rescues(zip_code: str) -> str:
    """
    Return a plain-English summary of pug rescues near zip_code
    Uses a hardcoded regional lookup keyed by the first digit of the zip —
    reliable for live demos with no external API dependency
    """
    zip_clean = zip_code.strip().replace(" ", "")
    region = zip_clean[0] if zip_clean and zip_clean[0].isdigit() else None
    rescues = PUG_RESCUES_BY_REGION.get(region, DEFAULT_RESCUES)

    lines = [
        f"{name} in {city}, {state} — {phone}" for name, city, state, phone in rescues
    ]
    summary = "; ".join(lines)

    pug_rescue_result = (
        f"Great news! I found {len(rescues)} pug rescue organizations near {zip_code}: "
        f"{summary}. I'd recommend calling ahead — availability changes quickly, "
        "and they can tell you about any pugs coming in soon too."
    )

    return pug_rescue_result


async def dispatch_function_call(
    fn: dict,
    deepgram_ws,
    state: CallState,
) -> None:
    """
    Handle a single function call from a FunctionCallRequest event
    Sends a FunctionCallResponse back to Deepgram for all functions
    except end_call, which is deferred until AgentAudioDone fires
    """
    fn_name = fn.get("name")
    fn_id = fn.get("id")
    logger.info(
        LogColor.wrap(
            LogColor.YELLOW, f"Function call: {fn_name} | args: {fn.get('arguments')}"
        )
    )

    if fn_name == "find_pug_rescues":
        args = json.loads(fn.get("arguments", "{}"))
        zip_code = args.get("zip_code", "")
        result = await find_pug_rescues(zip_code)
        logger.info(f"Rescue lookup result: {result}")

    elif fn_name == "end_call":
        state.ending_call = True
        state.end_call_fn_id = fn_id
        logger.info("end_call invoked — sending FunctionCallResponse immediately")
        await deepgram_ws.send(
            json.dumps(
                {
                    "type": "FunctionCallResponse",
                    "id": fn_id,
                    "name": "end_call",
                    "content": "Call ended.",
                }
            )
        )
        return

    else:
        result = "Function not implemented."

    await deepgram_ws.send(
        json.dumps(
            {
                "type": "FunctionCallResponse",
                "id": fn_id,
                "name": fn_name,
                "content": result,
            }
        )
    )


async def handle_deepgram(
    deepgram_ws,
    vonage_ws: WebSocket,
    original_uuid: str,
    state: CallState,
) -> None:
    """
    Loop 1: Deepgram → Vonage.
    Receives messages from Deepgram and reacts:
      - bytes               → forward PCM audio to Vonage (unless farewell is done)
      - UserStartedSpeaking → send CLEAR to Vonage (barge-in)
      - AgentAudioDone      → if ending_call, send deferred FunctionCallResponse + hang up
      - FunctionCallRequest → dispatch to find_pug_rescues or end_call
    """
    try:
        async for message in deepgram_ws:

            if isinstance(message, bytes):
                # Raw PCM audio from the AI agent
                # farewell_done blocks any audio after the farewell has played,
                # preventing a repeated farewell during the hangup window
                if not state.farewell_complete:
                    await vonage_ws.send_bytes(message)

            else:
                data = json.loads(message)
                event_type = data.get("type")
                event_role = data.get("role")

                # Handle color coding logs for demonstration purposes
                # YELLOW for event types
                # GREEN for role: assistant logs
                # MAGENTA for role: user logs
                if event_type != "LatencyReport":
                    logger.info(
                        LogColor.wrap(
                            LogColor.YELLOW,
                            f"Deepgram -> event type is {event_type}",
                        )
                    )
                if event_role == "assistant":
                    logger.info(LogColor.wrap(LogColor.GREEN, f"Deepgram -> {data}"))
                if event_role == "user":
                    logger.info(LogColor.wrap(LogColor.MAGENTA, f"Deepgram -> {data}"))

                if event_type == "UserStartedSpeaking":
                    # Barge-in: caller interrupted the agent mid-response
                    # Tell Vonage to discard its audio buffer immediately
                    await vonage_ws.send_text(json.dumps({"action": "clear"}))
                    logger.info(
                        LogColor.wrap(LogColor.RED, "CLEAR sent to Vonage (barge-in)")
                    )

                elif event_type == "AgentAudioDone":
                    # If the state is ending_call
                    # and AgentAudioDone has been fired off by Deepgram
                    # and if the agent has provided a farewell
                    # then hang up the call
                    if state.ending_call and original_uuid:
                        state.farewell_complete = True
                        logger.info(
                            LogColor.wrap(
                                LogColor.RED,
                                f"AgentAudioDone + ending_call — hanging up | UUID: {original_uuid}",
                            )
                        )
                        await asyncio.sleep(2)
                        try:
                            VONAGE_VOICE.hangup(original_uuid)
                            logger.info(
                                LogColor.wrap(
                                    LogColor.RED,
                                    f"Call hung up | UUID: {original_uuid}",
                                )
                            )
                        except Exception as exc:
                            logger.error(f"Hangup failed: {exc}")

                elif event_type == "FunctionCallRequest":
                    for fn in data.get("functions", []):
                        await dispatch_function_call(fn, deepgram_ws, state)

    except websockets.exceptions.ConnectionClosed:
        logger.info("Deepgram WebSocket closed")
        state.deepgram_websocket_open = False
