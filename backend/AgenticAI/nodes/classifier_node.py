import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from AgenticAI.llms.openai_llms import get_light_llm
from AgenticAI.utils.semantic_key_rags import key_descriptions

classifier_prompt = PromptTemplate(
    input_variables=["query", "telemetry_keys"],
    template="""
You are a UAV telemetry assistant. Your job is to classify user queries as either "factual" or "anomaly". 
You must also extract which telemetry keys (from this list: {telemetry_keys}) are directly relevant to the query (if any).

**Instructions:**
- If the user is asking about anomalies/issues in a specific subsystem (e.g., "in the GPS data"), include only that key in "target_keys".
- If the user is asking about the whole flight or anomalies in general, set "target_keys" to an empty list.
- For factual queries, target_keys should be an empty list.
- Only use keys from the provided list; if no relevant key is present, return an empty list.

**Factual query examples:**
- Query: "What was the highest altitude reached during the flight?"
  Label: {{"query_type": "factual"}}
- Query: "When did the GPS signal first get lost?"
  Label: {{"query_type": "factual"}}
- Query: "How long was the total flight time?"
  Label: {{"query_type": "factual"}}
- Query: "What was the maximum battery temperature?"
  Label: {{"query_type": "factual"}}
- Query: "List all critical errors that happened mid-flight."
  Label: {{"query_type": "factual"}}
- Query: "When was the first instance of RC signal loss?"
  Label: {{"query_type": "factual"}}

**Anomaly query examples:**
- Query: "Are there any anomalies in this flight?"
  Label: {{"query_type": "anomaly", "target_keys": []}}
- Query: "Can you spot any issues in the GPS data?"
  Label: {{"query_type": "anomaly", "target_keys": ["GPS"]}}
- Query: "Look for sudden changes in altitude, battery voltage, or inconsistent GPS lock."
  Label: {{"query_type": "anomaly", "target_keys": ["BARO", "BATT", "GPS"]}}
- Query: "Were there any abnormal events during the flight?"
  Label: {{"query_type": "anomaly", "target_keys": []}}
---
User Query: "{query}"

Telemetry Keys: {telemetry_keys}

---
Respond in **JSON** format like this:
{{
  "query_type": "factual" or "anomaly",
  "target_keys": []
}}
"""
)

classifier_chain = LLMChain(
    llm=get_light_llm(),
    prompt=classifier_prompt
)

def classifier_node(state: dict) -> dict:
    query = state["query"]
    telemetry_keys = list(key_descriptions.keys())

    response = classifier_chain.run({
        "query": query,
        "telemetry_keys": telemetry_keys
    })
    try:
        result = json.loads(response)
        state["query_type"] = result.get("query_type", "factual")
        target_keys = result.get("target_keys", [])
        state["target_keys"] = target_keys if target_keys else None
    except Exception as e:
        print("[classifier_node] Error parsing LLM response:", e, response)
        state["query_type"] = "factual"
        state["target_keys"] = None
    print("[classifier_node] Classified query:", state["query"], "as", state["query_type"])
    return state