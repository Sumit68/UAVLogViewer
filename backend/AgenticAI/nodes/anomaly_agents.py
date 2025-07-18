from AgenticAI.states.types import UAVBotState
from AgenticAI.llms.openai_llms import get_core_llm
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate

anomaly_prompt = PromptTemplate.from_template("""
You're an autonomous UAV anomaly detection agent.

User asked: "{query}"

Here's the structured summary of telemetry fields (CTUN, GPS, ERR, BATT):
{summary}

Please list any anomalies you detect. Cite field names, timestamps, and reasoning. Be precise.
""")

llm = get_core_llm()
anomaly_chain = LLMChain(llm=llm, prompt=anomaly_prompt)

def anomaly_agent_node(state: UAVBotState) -> UAVBotState:
    print(f"[anomaly_agent_node] Called with query: {state['query']!r}, query_type: {state.get('query_type')}", flush=True)
    summary = "..."

    if state.get("parsed_telemetry"):
        print(f"[anomaly_agent_node] parsed_telemetry keys: {list(state['parsed_telemetry'].keys())}", flush=True)
        gps_data = state["parsed_telemetry"].get("GPS", [])
        if gps_data:
            print(f"[anomaly_agent_node] GPS sample: {gps_data[:2]}", flush=True)
        gps_hdop = [m.get("HDop") for m in gps_data if "HDop" in m]
        err_msgs = [m.get("Message") for m in state["parsed_telemetry"].get("ERR", []) if "Message" in m]
        summary = f"GPS.HDOP: {gps_hdop[:10]}\nERR messages: {err_msgs}"

    output = anomaly_chain.run(query=state["query"], summary=summary)
    if "findings" not in state:
        state["findings"] = []
    state["findings"].append(output)
    state["final_response"] = output
    print(f"[anomaly_agent_node] final_response: {state['final_response']!r}", flush=True)
    return state
