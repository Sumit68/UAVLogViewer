from pymongo import MongoClient

def query_executor_node(state: dict) -> dict:
    llm_query = state.get("llm_query", {})
    if not llm_query:
        raise ValueError("No LLM-generated query found in state.")

    client = MongoClient("mongodb://localhost:27017/")
    db = client['telemetry_db']
    collection = db['telemetry_all']
    print("Executing query:", llm_query)
    # Check for aggregation query
    if "pipeline" in llm_query:
        pipeline = llm_query["pipeline"]
        if not isinstance(pipeline, list):
            raise ValueError("Invalid aggregation pipeline format.")
        results = list(collection.aggregate(pipeline))

    # Check for standard find query
    elif "query" in llm_query:
        mongo_query = llm_query.get("query", {})
        sort = llm_query.get("sort", None)
        limit = llm_query.get("limit", 10)

        cursor = collection.find(mongo_query)
        if sort:
            cursor = cursor.sort(sort)
        if limit:
            cursor = cursor.limit(limit)

        results = list(cursor)

    else:
        raise ValueError("LLM query must contain either 'query' or 'pipeline'.")

    # Store results in state
    state["query_results"] = results
    return state