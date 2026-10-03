import os
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

class GuardrailOutput(BaseModel):
    is_safe: bool
    reason: str

system_prompt = (
    "You are a Safety and Relevance Guardrail for a Travel Assistant System.\n"
    "Evaluate user input relevance to travel/tourism and ensure no harmful content.\n"
    "Set is_safe=True if safe/relevant, otherwise is_safe=False."
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{user_input}")
])

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

guardrail_chain = prompt | llm.with_structured_output(GuardrailOutput)

def check_input_guardrail(user_input: str) -> GuardrailOutput:
    return guardrail_chain.invoke({"user_input": user_input})