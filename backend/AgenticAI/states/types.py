from typing import Dict, Any, List, Literal, Optional
from typing_extensions import TypedDict  # Always use typing_extensions

class UAVBotState(TypedDict, total=False):
    query: str
    session_id: Optional[str]
    query_type: Literal["factual", "anomaly", "unknown"]
    target_keys: Optional[List[str]]
    factual_keys: Optional[List[str]]
    parsed_telemetry: Optional[Dict[str, List[Dict[str, Any]]]]
    llm_query: Optional[Dict[str, Any]]
    final_response: Optional[str]