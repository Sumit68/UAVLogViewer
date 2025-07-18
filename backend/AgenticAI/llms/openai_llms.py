from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
def get_light_llm():
    """Low-cost model for lightweight agents (field extractors, initial filters)."""
    return ChatOpenAI(
        model_name="gpt-3.5-turbo-0125",
        temperature=0.3,
        max_tokens=512,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )

def get_core_llm():
    """Higher accuracy model for final synthesis and complex reasoning."""
    return ChatOpenAI(
        model_name="gpt-4-1106-preview",
        temperature=0.3,
        max_tokens=1024,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )
