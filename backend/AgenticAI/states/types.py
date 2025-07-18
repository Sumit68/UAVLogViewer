from typing import Dict, Any, List, Literal, Optional, TypedDict

class UAVBotState(TypedDict, total=False):
    query: str
    query_type: Literal["factual", "anomaly", "unknown"]
    target_keys: Optional[List[str]]
    factual_keys: Optional[List[str]]
    parsed_telemetry: Optional[Dict[str, List[Dict[str, Any]]]]
    final_response: Optional[str]