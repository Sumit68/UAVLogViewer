from pymongo import MongoClient

def query_executor_node(state: dict) -> dict:
    llm_query = state.get("llm_query", {})
    if not llm_query:
        raise ValueError("No LLM-generated query found in state.")

    client = MongoClient("mongodb://localhost:27017/")
    db = client['telemetry_db']
    collection = db['telemetry_all']

    # Extract query, sort, limit from llm_query (with sensible defaults)
    mongo_query = llm_query.get("query", {})
    sort = llm_query.get("sort", None)
    limit = llm_query.get("limit", 10)  # Default to 10 if not specified

    cursor = collection.find(mongo_query)
    if sort:
        cursor = cursor.sort(sort)
    if limit:
        cursor = cursor.limit(limit)

    results = list(cursor)
    state["query_results"] = results
    return state
