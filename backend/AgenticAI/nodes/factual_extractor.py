from AgenticAI.states.types import UAVBotState
from AgenticAI.llms.openai_llms import get_light_llm
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

extractor_prompt = PromptTemplate.from_template("""
You're a telemetry analyst. The user asked: "{query}"

Below is structured telemetry data from a UAV flight:
{summary}

Based on the data, answer the user's question. Include specific field names and timestamps.
""")

llm = get_light_llm()
extractor_chain = LLMChain(llm=llm, prompt=extractor_prompt)

def factual_extractor_node(state: dict) -> dict:
    print(f"[factual_extractor_node] Called with query: {state['query']!r}, query_type: {state.get('query_type')}", flush=True)
    summary_text = ""

    # Use only the keys that were identified as relevant
    factual_keys = state.get("factual_keys", [])
    parsed_telemetry = state.get("parsed_telemetry", {})

    if not factual_keys:
        # fallback: summarize all
        factual_keys = list(parsed_telemetry.keys())

    for key in factual_keys:
        msgs = parsed_telemetry.get(key, [])
        # Show only a few samples, for context (avoid flooding the LLM)
        sample = msgs[:3] if msgs else "No data available"
        summary_text += f"\nKey: {key}, sample data: {sample}"

    print(f"[factual_extractor_node] Summary text: {summary_text}", flush=True)
    response = extractor_chain.run(query=state["query"], summary=summary_text)
    state["final_response"] = response
    print(f"[factual_extractor_node] final_response: {state['final_response']!r}", flush=True)
    return state

