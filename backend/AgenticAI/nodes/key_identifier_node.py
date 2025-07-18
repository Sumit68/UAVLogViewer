from AgenticAI.utils.semantic_key_rags import identify_relevant_keys

def key_identifier_node(state: dict) -> dict:
    query = state["query"]
    keys = identify_relevant_keys(query)
    state["factual_keys"] = keys
    print(f"[key_identifier_node] Identified keys: {keys}", flush=True)
    return state
