from langchain.chat_models import ChatOpenAI 
import os
from dotenv import load_dotenv

load_dotenv()

def get_mistral_llm():
    return ChatOpenAI(
        model_name="mistralai/mistral-7b-instruct",  # or another OpenRouter-supported model
        temperature=0.3,
        max_tokens=512,
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1"  # Required to route to OpenRouter
    )

def get_qwen_llm():
    return ChatOpenAI(
        model_name="qwen/qwen3-235b-a22b-07-25:free",
        temperature=0.3,
        max_tokens=512,
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1"  # Ensures calls go through OpenRouter
    )

def get_deepseek_llm():
    return ChatOpenAI(
        model_name="tngtech/deepseek-r1t2-chimera:free",
        temperature=0.3,
        max_tokens=2048,
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1"  # Ensures calls go through OpenRouter
    )