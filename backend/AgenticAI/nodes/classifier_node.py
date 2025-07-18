from AgenticAI.states.types import UAVBotState
from AgenticAI.utils.query_classifier import classify_query
from AgenticAI.utils.semantic_key_rags import identify_relevant_keys

def classify_query(query: str) -> str:
    if "anomaly" in query.lower():
        return "anomaly"
    elif "altitude" in query.lower() or "battery" in query.lower():
        return "factual"
    return "unknown"

# def classifier_node(state: UAVBotState) -> UAVBotState:
#     print(f"[classifier_node] Called with query: {state['query']!r}", flush=True)
#     state["query_type"] = classify_query(state["query"])
#     print(f"[classifier_node] Classified as: {state['query_type']}", flush=True)
#     return state

def classifier_node(state: dict) -> dict:
    query = state["query"].lower()
    anomaly_keys = ["anomaly", "issue", "problem", "error", "fail", "glitch"]
    # List your telemetry keys here (can use ["BAT", "GPS", "ALT"] etc.)
    key_names = ["battery", "bat", "gps", "altitude", "alt", "speed", "arspd", "fuel"]

    if any(word in query for word in anomaly_keys):
        state["query_type"] = "anomaly"
        # Try to spot which subsystem is targeted (if any)
        target = [k for k in key_names if k in query]
        if target:
            state["target_keys"] = target
        else:
            state["target_keys"] = None
    else:
        state["query_type"] = "factual"
    return state
