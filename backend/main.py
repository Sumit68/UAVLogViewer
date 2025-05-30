import json
from typing import List, Optional
from pymavlink import mavutil
from fastapi.responses import JSONResponse
from fastapi import FastAPI, UploadFile, File, Request
import os, uuid
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_core.language_models.chat_models import SimpleChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.callbacks import CallbackManagerForLLMRun
import requests
from dotenv import load_dotenv

load_dotenv()

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

# Session-specific conversation chains
session_chains = {}

class UAVInfoBot(SimpleChatModel):
    model: str = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    temperature: float = 0.7
    together_api_key: Optional[str] = None

    def __init__(
        self,
        model: str = "mistralai/Mixtral-8x7B-Instruct-v0.1",
        temperature: float = 0.7,
        api_key: Optional[str] = None,
    ):
        super().__init__()
        self.model = model
        self.temperature = temperature
        self.together_api_key = api_key or os.getenv("TOGETHER_API_KEY")

    def _call(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        print("Calling UAVInfoBot with messages:", messages)
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system" if isinstance(m, SystemMessage)
                    else "user" if isinstance(m, HumanMessage)
                    else "assistant",
                    "content": m.content,
                }
                for m in messages
            ],
            "temperature": self.temperature,
            "max_tokens": 512,
        }

        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.together_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

        response_json = response.json()
        print("UAVInfoBot response:", response_json)
        content = response_json["choices"][0]["message"]["content"]
        return content

    @property
    def _llm_type(self) -> str:
        return "uav-info-bot"

def get_conversation(session_id):
    if session_id not in session_chains:
        memory = ConversationBufferMemory()
        session_chains[session_id] = ConversationChain(llm=UAVInfoBot(api_key=os.getenv("TOGETHER_API_KEY")), memory=memory)
    return session_chains[session_id]

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

        print(f"File uploaded: {file.filename} to {path}")
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
        session_id = data.get("session_id") # What is session_id is null?

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

        conv = get_conversation(session_id)
        # conv.memory.chat_memory.messages = [
        #     SystemMessage(content=system_prompt),
        #     HumanMessage(content=message)
        # ]
        messages = []

        if not conv.memory.chat_memory.messages:
            messages.append(SystemMessage(content=system_prompt))

        messages.extend(conv.memory.chat_memory.messages)

        messages.append(HumanMessage(content=message))

        reply = conv.llm._call(messages)

        conv.memory.chat_memory.messages.append(HumanMessage(content=message))
        conv.memory.chat_memory.messages.append(AIMessage(content=reply))

        return {"response": reply, "session_id": session_id}
    except Exception as e:
        print("Chat error in backend:", str(e))
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
        return parsed_data

    except Exception as e:
        return {"error": str(e)}
