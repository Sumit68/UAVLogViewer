# AgentiAI/graphs/uav_graph.py

from langgraph.graph import StateGraph, END
from AgenticAI.states.types import UAVBotState
from AgenticAI.nodes.classifier_node import classifier_node
from AgenticAI.nodes.factual_extractor import factual_extractor_node
from AgenticAI.nodes.anomaly_agents import anomaly_agent_node
from AgenticAI.nodes.key_identifier_node import key_identifier_node

def route_query_type(state: dict) -> str:
    if state.get("query_type") == "factual":
        return "factual"
    elif state.get("query_type") == "anomaly":
        return "anomaly"
    return END

def build_uav_graph():
    builder = StateGraph(dict)

    builder.add_node("classify", classifier_node)
    builder.add_node("key_identifier", key_identifier_node)
    builder.add_node("factual", lambda state: state)  # Dummy node for routing
    builder.add_node("factual_extractor", factual_extractor_node)
    builder.add_node("anomaly", anomaly_agent_node)

    builder.set_entry_point("classify")
    builder.add_conditional_edges("classify", route_query_type)

    # Route factual queries to key_identifier, then to factual_extractor
    builder.add_edge("factual", "key_identifier")
    builder.add_edge("key_identifier", "factual_extractor")
    builder.add_edge("factual_extractor", END)

    builder.add_edge("anomaly", END)

    return builder.compile()
