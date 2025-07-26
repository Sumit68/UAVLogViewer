from AgenticAI.states.types import UAVBotState
from AgenticAI.llms.openai_llms import get_light_llm
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from AgenticAI.llms.openrouter_llms import get_mistral_llm

extractor_prompt = PromptTemplate.from_template("""
You are a UAV telemetry analyst.

The user asked: "{query}"

The database query returned the following result(s):

{results}

Explain the result to a non-technical user in clear, plain language. Focus on what the result means for the flight or drone performance. If there are important numbers, explain what they represent.
""")

llm = get_mistral_llm()
extractor_chain = LLMChain(llm=llm, prompt=extractor_prompt)

def factual_extractor_node(state: dict) -> dict:
    print(f"[factual_extractor_node] Called with query: {state['query']!r}, query_type: {state.get('query_type')}", flush=True)
    
    query_results = state.get("query_results", [])
    # Convert to JSON for context (pprint for readability or use json.dumps for stricter format)
    from pprint import pformat
    if not query_results:
        results_text = "No data was found for this query."
    else:
        # Optionally, you can limit and clean up fields for clarity
        sample_results = [{k: v for k, v in doc.items() if k != "_id"} for doc in query_results[:5]]
        results_text = pformat(sample_results)
    
    response = extractor_chain.run(query=state["query"], results=results_text)
    state["final_response"] = response
    return state