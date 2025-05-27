# UAV Telemetry Agentic Chatbot

This project enables natural language interaction with UAV `.bin` telemetry logs using LangChain, Together API, and FastAPI. It processes telemetry data using `pymavlink`, and responds agentically to user queries while maintaining session memory.

---

## 🚀 Features

* Upload `.bin` UAV logs
* Parse MAVLink messages with `pymavlink`
* Interact via natural language
* Retains conversational memory per session
* Uses Together API (Mistral) through custom LangChain integration

---

## 🛠️ Tech Stack

* FastAPI
* pymavlink
* LangChain with `ConversationBufferMemory`
* Together API with custom `SimpleChatModel`

---

## ⚡ Installation

### 1. Clone the repo

```bash
git clone https://github.com/Sumit68/UAVLogViewer.git
cd UAVLogViewer/backend
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add `.env` file

Create a `.env` file:

```env
TOGETHER_API_KEY=your_together_api_key_here
```

---

## 🌐 Run Locally

```bash
python run.py
```

Visit: [http://localhost:8000/docs](http://localhost:8000/docs) for API documentation

---

## 📂 Folder Structure

```
├── backend/
│   ├── main.py                # FastAPI backend
│   ├── uploaded_logs/         # Directory for uploaded telemetry logs
│   ├── .env                   # Environment variables (e.g., Together API key)
│   └── requirements.txt       # Trimmed down to minimal dependencies
```

---

## 🔄 Sample API Usage

### Upload telemetry log

```
POST /api/upload
form-data:
  file: <your .bin file>
  session_id: optional
```

### Ask a question

```
POST /api/chat
JSON body:
  {
    "message": "Any anomalies in flight?",
    "session_id": "same-as-above"
  }
```

---

## 🙏 Acknowledgment

Made by [Sumit Kothari](https://github.com/Sumit68)

---
