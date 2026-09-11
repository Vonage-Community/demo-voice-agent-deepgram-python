from dataclasses import dataclass

@dataclass
class CallState:
    dg_ws_open:     bool = False
    ending_call:    bool = False
    farewell_done:  bool = False
    end_call_fn_id: str | None = None
