from AgenticAI.llms.openrouter_llms import get_deepseek_llm
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from motor.motor_asyncio import AsyncIOMotorClient
from langchain_core.output_parsers import StrOutputParser
from AgenticAI.utils.projections import get_projection
import asyncio

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "telemetry_db"
COLL_NAME = "telemetry_all"

async def fetch_key_view(coll, session_id: str, key: str, head_n: int = 2, tail_n: int = 2):
    projection = get_projection(key)

    # Get head (oldest N)
    head_cursor = coll.find(
        {"session_id": session_id, "msg_type": key},
        projection=projection
    ).sort("TimeUS", 1).limit(head_n)
    head = await head_cursor.to_list(length=head_n)

    # Get tail (newest N)
    tail_cursor = coll.find(
        {"session_id": session_id, "msg_type": key},
        projection=projection
    ).sort("TimeUS", -1).limit(tail_n)
    tail = await tail_cursor.to_list(length=tail_n)

    # Get stats (min/max TimeUS + count)
    stats_pipeline = [
        {"$match": {"session_id": session_id, "msg_type": key}},
        {"$project": {"TimeUS": 1}}, 
        {"$group": {
            "_id": None,
            "count": {"$sum": 1},
            "min_time": {"$min": "$TimeUS"},
            "max_time": {"$max": "$TimeUS"}
        }}
    ]
    stats_docs = await coll.aggregate(stats_pipeline).to_list(length=1)
    stats = stats_docs[0] if stats_docs else {}

    return {
        "head": head,
        "tail": tail,
        "stats": {
            "count": stats.get("count", 0),
            "min_time": stats.get("min_time"),
            "max_time": stats.get("max_time"),
            "duration": (
                stats.get("max_time") - stats.get("min_time")
                if stats.get("max_time") is not None and stats.get("min_time") is not None
                else None
            )
        }
    }

async def anomaly_judge_llm(key, data, llm):
    print(f"[anomaly_judge_llm] Analyzing key: {key}", flush=True)
    prompt_template = PromptTemplate.from_template(
       "For telemetry key '{key}', here is a compact view:\n"
        "- Stats: {stats}\n"
        "- Head samples (oldest): {head}\n"
        "- Tail samples (newest): {tail}\n\n"
        "Identify any anomalies (ranges, spikes, outliers, discontinuities, etc). If yes, describe where and why. If no, state that there are no anomalies.\n"
    )
    prompt = prompt_template.format(
        key=key,
        stats=data.get("stats"),
        head=data.get("head"),
        tail=data.get("tail")
    )
    # chain = prompt | llm 
    chain = LLMChain(llm=llm, prompt=prompt_template)
    if chain is None:
        print(f"[ERROR] Chain composition failed for key {key}")
        return "Chain failed"

    try:
        result = await chain.ainvoke({
            "key": key,
            "stats": data.get("stats"),
            "head": data.get("head"),
            "tail": data.get("tail")
        })
    except Exception as e:
        print(f"[anomaly_judge_llm] Exception for key {key}: {e}")
        result = "Error in LLM"
    return result

async def run_anomaly_agents(session_id: str, keys, target_key=None):
    print(f"[run_anomaly_agents] Called with keys: {keys}, target_key: {target_key}", flush=True)
    llm = get_deepseek_llm()
    results = {}

    # if not keys or not isinstance(keys, (list, tuple)):
    #     print("[run_anomaly_agents] keys is None or not a list/tuple!", flush=True)
    #     return results

    client = AsyncIOMotorClient(MONGO_URI)
    coll = client[DB_NAME][COLL_NAME]
    print("session_id:", session_id, flush=True)
    async def analyze_key(key: str):
        view = await fetch_key_view(coll, session_id, key)
        return await anomaly_judge_llm(key, view, llm)

    # Case 1: specific key
    if target_key:
        if target_key not in keys:
            print(f"[run_anomaly_agents] target_key {target_key} not in provided keys; skipping.", flush=True)
            return results
        results[target_key] = await analyze_key(target_key)
    else:
        tasks = {key: asyncio.create_task(analyze_key(key)) for key in keys}
        for key, task in tasks.items():
            results[key] = await task

    print(f"[run_anomaly_agents] Results: {results}", flush=True)
    client.close()
    return results