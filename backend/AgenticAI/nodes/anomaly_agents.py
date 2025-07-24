from AgenticAI.llms.openrouter_llms import get_deepseek_llm
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
import asyncio

async def anomaly_judge_llm(key, data, llm):
    print(f"[anomaly_judge_llm] Called for key: {key}, data sample: {str(data)[:300]}", flush=True)
    prompt_template = PromptTemplate.from_template(
        "For telemetry key '{key}', here is the associated data:\n"
        "{data}\n\n"
        "Based on these, are there any anomalies? If yes, describe where and why. If no, state that there are no anomalies.\n"
    )
    prompt = prompt_template.format(key=key, data=data)
    print(f"[anomaly_judge_llm] Final prompt:\n{prompt}")
    chain = LLMChain(llm=llm, prompt=prompt_template)
    try:
        result = await chain.arun({"key": key, "data": data})
    except Exception as e:
        print(f"Exception in LLM call for key {key}: {e}")
        result = None
    print(f"[anomaly_judge_llm] LLM result for key {key}: {result}", flush=True)
    return result

async def run_anomaly_agents(session_telemetry, keys, target_key=None):
    print(f"[run_anomaly_agents] Called with keys: {keys}, target_key: {target_key}", flush=True)
    llm = get_deepseek_llm()
    results = {}

    # Defensive: Ensure session_telemetry is a dict and keys is iterable
    if not isinstance(session_telemetry, dict):
        print("[run_anomaly_agents] session_telemetry is not a dict!", flush=True)
        return results
    if not keys or not isinstance(keys, (list, tuple)):
        print("[run_anomaly_agents] keys is None or not a list/tuple!", flush=True)
        return results

    # Helper: Analyze a single key
    async def analyze_key(key):
        entries = session_telemetry.get(key, [])
        print(f"[run_anomaly_agents] Analyzing key: {key}, entries count: {len(entries)}", flush=True)
        sample_data = entries[:5] if entries else "No data available"
        return await anomaly_judge_llm(key, sample_data, llm)

    # Case 1: Query is about a specific key
    if target_key and target_key in session_telemetry:
        print(f"[run_anomaly_agents] Using target_key: {target_key}", flush=True)
        results[target_key] = await analyze_key(target_key)
    # Case 2: Analyze all keys in the provided list
    else:
        tasks = {key: asyncio.create_task(analyze_key(key))
                 for key in keys[:] if key in session_telemetry}
        for key, task in tasks.items():
            results[key] = await task
    print(f"[run_anomaly_agents] Results keys: {list(results.keys())}", flush=True)
    return results
