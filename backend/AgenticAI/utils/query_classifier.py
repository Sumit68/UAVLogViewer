from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from AgenticAI.llms.openai_llms import get_light_llm

classifier_prompt = PromptTemplate.from_template("""
Classify the user query into one of the following types:
- factual
- anomaly
- unknown

User query: "{query}"
Type:
""")

classifier_chain = LLMChain(llm=get_light_llm(), prompt=classifier_prompt)

def classify_query(query: str) -> str:
    result = classifier_chain.run(query=query).strip().lower()
    if "factual" in result:
        return "factual"
    elif "anomaly" in result:
        return "anomaly"
    else:
        return "unknown"
