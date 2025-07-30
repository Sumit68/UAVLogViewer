from AgenticAI.utils.semantic_key_rags import identify_relevant_keys

def key_identifier_node(state: dict) -> dict:
    query = state["query"]
    keys = identify_relevant_keys(query)
    state["factual_keys"] = keys
    print("[key_identifier_node] Identified keys for query:", query, "->", keys)
    return state
