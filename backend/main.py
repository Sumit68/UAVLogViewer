# backend/main.py

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymavlink import mavutil
import requests
import json
import os
import uuid
from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response

load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
UPLOAD_DIR = "uploaded_logs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


app = FastAPI()

class LargeUploadMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        request._receive = request.receive  # ensure it can be read
        return await call_next(request)

app.add_middleware(LargeUploadMiddleware)
# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session memory and telemetry
sessions = {}  # session_id -> conversation history
session_telemetry = {}  # session_id -> parsed telemetry

@app.post("/api/upload")
async def upload_log(file: UploadFile = File(...), session_id: str = None):
    try:
        if not session_id:
            session_id = str(uuid.uuid4())

        filename = f"{uuid.uuid4()}_{file.filename}"
        path = os.path.join(UPLOAD_DIR, filename)
        contents = await file.read()
        with open(path, "wb") as f:
            f.write(contents)

        print(f"File uploaded: {filename} to {path}")
        telemetry = parse_telemetry(path)

        if not telemetry or "error" in telemetry:
            return JSONResponse(
                content={
                    "success": False,
                    "message": telemetry.get("error", "Failed to parse telemetry."),
                    "session_id": session_id
                },
                status_code=200
            )

        session_telemetry[session_id] = telemetry

        return JSONResponse(
            content={
                "success": True,
                "message": "File uploaded and telemetry parsed",
                "session_id": session_id
            },
            status_code=200
        )
    except Exception as e:
        print("Upload error in backend:", str(e))
        return JSONResponse(
            content={
                "success": False,
                "message": str(e),
                "session_id": session_id or ""
            },
            status_code=200
        )

@app.post("/api/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message")
        session_id = data.get("session_id")

        telemetry = session_telemetry.get(session_id, {})

        sample_data = {}
        for key in ["GPS", "BAT", "ERR", "RCIN", "BARO", "MSG"]:
            if key in telemetry and isinstance(telemetry[key], list):
                sample_data[key] = telemetry[key][:3]  # take a few entries

        system_prompt = (
            "You are an intelligent UAV telemetry assistant.\n"
            "You have access to telemetry logs parsed from MAVLink .bin files.\n"
            "Refer to ArduPilot's official documentation for MAVLink logs: https://ardupilot.org/plane/docs/logmessages.html\n"
            "Use this data to answer flight-specific questions.\n"
            "If the user asks about anomalies or system health, reason about:\n"
            "- Sudden changes in GPS altitude or fix type\n"
            "- Battery voltage drops or temperature spikes (BAT)\n"
            "- Critical error messages (ERR with severity >= 4)\n"
            "- RC signal loss (RCIN anomalies)\n"
            "Avoid overexplaining when not necessary. For acknowledgments like 'ok', respond briefly and politely.\n"
        )

        system_prompt += f"\n\nSample telemetry:\n{json.dumps(sample_data, default=str)[:2000]}"

        history = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]

        import requests
        TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                "messages": history,
                "temperature": 0.7,
                "max_tokens": 512
            }
        )
        reply = response.json()["choices"][0]["message"]["content"]

        return {"response": reply, "session_id": session_id}
    except Exception as e:
        print("Chat error:", str(e))
        return JSONResponse(content={"response": "Internal server error.", "session_id": session_id}, status_code=500)

def parse_telemetry(filepath):
    try:
        mav = mavutil.mavlink_connection(filepath, dialect="ardupilotmega", robust_parsing=True)
        parsed_data = {}

        while True:
            msg = mav.recv_match(blocking=True)
            if msg is None:
                break

            msg_type = msg.get_type()
            if msg_type == "FMT":
                continue

            try:
                msg_dict = msg.to_dict()
            except Exception:
                continue

            for key, value in msg_dict.items():
                if isinstance(value, bytes):
                    msg_dict[key] = value.decode(errors="ignore")
                elif hasattr(value, "tolist"):
                    msg_dict[key] = value.tolist()

            if msg_type not in parsed_data:
                parsed_data[msg_type] = []

            parsed_data[msg_type].append(msg_dict)

        print("Parsed message types:", list(parsed_data.keys()))
        return parsed_data

    except Exception as e:
        print("Error parsing telemetry:", str(e))
        return {"error": str(e)}
