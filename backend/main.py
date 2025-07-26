# backend/main.py

import os, uuid, json
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from AgenticAI.utils.telemetry_parser import parse_telemetry
from AgenticAI.graphs.uav_graph import build_uav_graph
from AgenticAI.states.types import UAVBotState

load_dotenv(dotenv_path="./.env")

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_logs"
session_telemetry = {}
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Load LangGraph
graph = build_uav_graph()

@app.post("/api/upload")
async def upload_log(file: UploadFile = File(...), session_id: str = None):
    try:
        if not session_id:
            session_id = str(uuid.uuid4())

        filename = f"{session_id}_{file.filename}"
        path = os.path.join(UPLOAD_DIR, filename)
        contents = await file.read()
        with open(path, "wb") as f:
            f.write(contents)

        print(f"File uploaded: {file.filename} to {path}")
        telemetry = parse_telemetry(path, session_id=session_id)

        if not telemetry or "error" in telemetry:
            return JSONResponse(
                content={"success": False, "message": telemetry.get("error", "Failed to parse telemetry."), "session_id": session_id},
                status_code=200,
            )

        session_telemetry[session_id] = telemetry

        return JSONResponse(
            content={"success": True, "message": "File uploaded and telemetry parsed", "session_id": session_id},
            status_code=200,
        )
    except Exception as e:
        print("Upload error:", str(e))
        return JSONResponse(content={"success": False, "message": str(e), "session_id": session_id or ""}, status_code=200)


@app.post("/api/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "")
        session_id = data.get("session_id", "")

        telemetry = session_telemetry.get(session_id)
        if not telemetry:
            return JSONResponse(content={"response": "No telemetry data found for this session.", "session_id": session_id}, status_code=400)

        state = {"query": message, "parsed_telemetry": telemetry}
        result = await graph.ainvoke(state) 
        if not result.get("final_response"):
            return JSONResponse(
                content={"response": "Sorry, I could not generate an answer for your query.", "session_id": session_id},
                status_code=200,
            )

        return {"response": result["final_response"], "session_id": session_id}
    except Exception as e:
        print("Chat error:", str(e), flush=True)
        return JSONResponse(content={"response": "Internal server error.", "session_id": session_id}, status_code=500)
