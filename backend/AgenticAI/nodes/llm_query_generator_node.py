import json
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from AgenticAI.llms.openai_llms import get_light_llm

# Example prompt template (customize as needed)
PROMPT_TEMPLATE = PromptTemplate.from_template(
    """You are an expert in writing MongoDB queries.
User asked: "{query}"
The most relevant telemetry fields may be: {factual_keys}
You should use these keys if they are relevant, but feel free to use others as needed.
List of all the telemetry keys: {telemetry_keys}
Structure of Data in MongoDB is as below:
{{
  "_id": {{
    "$oid": "68843aa003522bd1e0a97d25"
  }},
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
  "session_id": "09e15016-860f-4a69-a1e5-da3a9a9aa049"
}}
Return the query as a JSON object for use in PyMongo. Example:
{{
    "query": {{"session_id": {session_id}, "msg_type": "GPS"}},
    "sort": [["Alt", -1]],
    "limit": 1
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
        "telemetry_keys": list(state.get("parsed_telemetry", {}).keys())
    }
    llm_output = llm_chain.run(prompt_vars)
    # Parse and store
    state["llm_query"] = parse_llm_output(llm_output)
    print(state["llm_query"])
    return state