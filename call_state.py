from dataclasses import dataclass

@dataclass
class CallState:
    deepgram_websocket_open:     bool = False
    ending_call:    bool = False
    farewell_complete:  bool = False
    end_call_fn_id: str | None = None
