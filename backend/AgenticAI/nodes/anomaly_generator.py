# AgenticAI/nodes/anomaly_generator.py
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from AgenticAI.llms.openrouter_llms import get_deepseek_llm

def anomaly_generator_node(state):
    anomaly_results = state.get("anomaly_results", {})
    user_query = state.get("query", "")

    # Create a readable summary to prompt LLM
    results_text = "\n".join([f"{k}: {v}" for k, v in anomaly_results.items()])

    # Use a PromptTemplate for LLMChain (required by langchain)
    prompt_template = PromptTemplate.from_template(
        "User asked: {query}\n"
        "Here are the anomaly detection results from different telemetry keys:\n"
        "{results_text}\n\n"
        "Generate a clear, concise natural language summary for the user. "
        "Highlight any detected anomalies, their likely causes, and what the user should pay attention to."
    )

    llm = get_deepseek_llm()
    chain = LLMChain(llm=llm, prompt=prompt_template)
    report = chain.run({"query": user_query, "results_text": results_text})

    state["final_response"] = report
    return state
