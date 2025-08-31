# UAV Telemetry Agentic Chatbot

An **agentic AI system** for analyzing UAV telemetry logs (`.bin` files).  
It leverages **LangGraph**, **MongoDB**, and **LLMs** to answer factual queries and detect anomalies in UAV flight data.

---

## 🚀 Features

- **Agentic Workflow** – Uses LangGraph nodes for query classification and multi-agent execution.
- **Telemetry Parsing** – Extracts structured data from UAV .bin logs.
- **Factual Queries** – Identifies relevant telemetry keys and retrieves precise answers.
- **Anomaly Detection** – A collection of specialized agents, each dedicated to analyzing specific telemetry keys (e.g., GPS, BAT, RCIN, HEAT), designed to detect irregular patterns and anomalies in the data.
- **MongoDB Integration** → Efficiently stores parsed telemetry in a structured way, enabling faster lookups and scoped queries rather than repeatedly scanning large .bin logs.

- **Smart Query Execution** → The system computes queries effectively by combining semantic key identification with MongoDB retrieval, ensuring accurate and low-latency answers.
- **Natural Language Interface** – Users ask questions directly about flight performance, anomalies, or metrics.
**LLM Support**:  
  - OpenAI models (via `openai_llms.py`).  
  - OpenRouter models (via `openrouter_llms.py`).
- **Scalable Backend**: Modular nodes and agents for flexible graph-based reasoning.
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
OPENAI_API_KEY=your_openai_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key
```

---
### 4. MongoDB Setup (Using Docker)

If you don’t have MongoDB installed locally, you can set it up with Docker:

**Pull the MongoDB Docker Image**
```bash
docker pull mongodb/mongodb-community-server:latest
```

Run the Image as a Container
```bash
docker run --name mongodb -p 27017:27017 -d mongodb/mongodb-community-server:latest
```
The -p 27017:27017 flag maps the container’s port to your host machine, so you can connect to MongoDB with:
mongodb://localhost:27017

Check that the Container is Running
```bash
docker container ls
```

## 🌐 Run Locally

```bash
python run.py
```

Visit: [http://localhost:8000/docs](http://localhost:8000/docs) for API documentation

---

## 🌐 Run Frontend

After setting up and running the backend:

```bash
# go back to the project root (parent of backend/)
cd ..
```

```bash
# install dependencies
npm install

# serve with hot reload at localhost:8080
npm run dev

# build for production with minification
npm run build
```


## 📂 Project Structure

```bash
UAVLogViewer/
│
├── backend/
│   ├── agenticAI/                 # Core agentic reasoning
│   │   └── uav_graph.py           # LangGraph pipeline definition
│   │
│   ├── lms/
│   │   ├── openai_llms.py         # OpenAI integration
│   │   └── openrouter_llms.py     # OpenRouter integration
│   │
│   ├── nodes/                     # LangGraph nodes
│   │   ├── classifier_node.py     # Classifies factual vs anomaly queries
│   │   ├── key_identifier_node.py # Maps user queries to telemetry keys
│   │   ├── factual_extractor.py   # Factual query handler
│   │   ├── anomaly_agent_node.py  # Routes anomaly checks
│   │   ├── anomaly_agents.py      # Specialized anomaly detectors
│   │   ├── anomaly_generator.py   # Synthesizes anomaly responses
│   │   ├── lm_query_generator_node.py # Generates refined LM queries
│   │   └── query_executer_node.py # Executes structured queries
│   │
│   ├── states/
│   │   └── types.py               # Shared types and state definitions
│   │
│   ├── utils/
│   │   ├── projections.py         # Data projections for telemetry analysis
│   │   ├── query_classifier.py    # Semantic query classification
│   │   ├── semantic_key_rags.py   # Key-level retrieval for telemetry
│   │   └── telemetry_parser.py    # Parses UAV .bin logs
│   │
│   └── __init__.py
│
└── README.md

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
