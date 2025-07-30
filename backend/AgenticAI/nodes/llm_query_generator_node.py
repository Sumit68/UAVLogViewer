import json
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from AgenticAI.llms.openai_llms import get_light_llm
from AgenticAI.utils.semantic_key_rags import key_descriptions

# Example prompt template (customize as needed)
PROMPT_TEMPLATE = PromptTemplate(
    input_variables=["query", "factual_keys", "telemetry_keys", "session_id"],
    template="""
You are an expert in writing MongoDB queries for telemetry data analysis.
Your goal is to convert the user's question into a valid PyMongo query. This can be a simple query or an aggregation pipeline depending on the need.

User asked: "{query}"

Relevant telemetry fields: {factual_keys}
All telemetry keys: {telemetry_keys}

Structure of a telemetry document in MongoDB:
{{
  "_id": {{ "$oid": "68843aa003522bd1e0a97d25" }},
  "mavpackettype": "GPS",
  "TimeUS": 73816825,
  "I": 0,
  "Status": 1,
  "GMS": 7800,
  "GWk": 0,
  "NSats": 0,
  "HDop": 99.99,
  "Lat": 0,
  "Lng": 0,
  "Alt": -17,
  "Spd": 0,
  "GCrs": 0,
  "VZ": 0,
  "Yaw": 0,
  "U": 1,
  "msg_type": "GPS",
  "session_id": "{session_id}"
}}

--- Instructions ---
1. Always filter by the session_id: "{session_id}"
2. Use simple queries (query/sort/limit) for max/min value or first/last message.
3. Use aggregation (pipeline) for computations like duration, counts, averages, etc.
4. If the query is ambiguous, make a reasonable assumption and proceed.

--- Examples ---

Q: "What was the maximum altitude?"
A:
{{
  "query": {{"session_id": "{session_id}", "msg_type": "GPS"}},
  "sort": [["Alt", -1]],
  "limit": 1
}}

Q: "How long was the total flight?"
A:
{{
  "pipeline": [
    {{ "$match": {{"session_id": "{session_id}"}} }},
    {{ "$group": {{
      "_id": null,
      "start": {{ "$min": "$TimeUS" }},
      "end": {{ "$max": "$TimeUS" }}
    }} }},
    {{ "$project": {{
      "_id": 0,
      "duration": {{ "$subtract": ["$end", "$start"] }}
    }} }}
  ]
}}

Q: "What was the average battery voltage?"
A:
{{
  "pipeline": [
    {{ "$match": {{"session_id": "{session_id}", "msg_type": "BAT"}} }},
    {{ "$group": {{
      "_id": null,
      "avg_voltage": {{ "$avg": "$Volt" }}
    }} }}
  ]
}}

Now respond with the correct query in JSON format.
Return the result as a JSON object for use in PyMongo.

Use **this format** for simple queries:
{{
  "query": {{"session_id": "{session_id}", "msg_type": "GPS"}},
  "sort": [["Alt", -1]],
  "limit": 1
}}

Use **this format** for aggregation queries:
{{
  "pipeline": [
    {{ "$match": {{"session_id": "{session_id}"}} }},
    {{ "$group": {{
      "_id": null,
      "min_time": {{ "$min": "$TimeUS" }},
      "max_time": {{ "$max": "$TimeUS" }}
    }} }},
    {{ "$project": {{
      "duration": {{ "$subtract": ["$max_time", "$min_time"] }}
    }} }}
  ]
}}
"""
)

llm = get_light_llm()
llm_chain = LLMChain(llm=llm, prompt=PROMPT_TEMPLATE)

def parse_llm_output(output):
    return json.loads(output)

def llm_query_generator_node(state: dict) -> dict:
    query = state["query"]
    factual_keys = state.get("factual_keys", [])
    session_id = state.get("session_id", "")

    prompt_vars = {
        "query": query,
        "factual_keys": factual_keys,
        "session_id": session_id,
        "telemetry_keys": list(key_descriptions.keys())
    }
    llm_output = llm_chain.run(prompt_vars)
    # Parse and store
    state["llm_query"] = parse_llm_output(llm_output)
    print(state["llm_query"])
    return state