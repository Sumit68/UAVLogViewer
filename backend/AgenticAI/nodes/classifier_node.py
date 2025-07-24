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
