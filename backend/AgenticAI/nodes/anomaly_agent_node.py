from AgenticAI.nodes.anomaly_agents import run_anomaly_agents

async def anomaly_agent_node(state):
    session_id = state.get("session_id", "")
    target_keys = state.get("target_keys")
    keys = [
    "GPS",
    "BAT",
    "POWR",
    "ERR",
    "IMU",
    "VIBE",
    "MAG",
    "RCIN",
    "RCOU",
    "MODE",
    "MSG",
    "CTUN",
    "HEAT"
]

    # Pick just one if there's a target, else check all in 'keys'
    if target_keys and isinstance(target_keys, list) and len(target_keys) == 1:
        target_key = target_keys[0]
    else:
        target_key = None

    # Call your anomaly agent runner
    anomaly_results = await run_anomaly_agents(session_id, keys, target_key=target_key)

    # Add results to state for next node or response
    state["anomaly_results"] = anomaly_results
    return state
