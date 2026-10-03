import os
from typing import Literal
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

# Danh sách các Agent quản lý bởi Supervisor
members = [
    "TransportAgent",
    "AccommodationAgent",
    "WeatherAgent",
    "SocialReviewAgent",
    "BudgetAgent",
    "ItineraryAgent"
]

system_prompt = (
    "You are the Supervisor (Router & Coordinator) of a Multi-Agent Travel System.\n"
    "Based on the user's input and conversation history, analyze the context and select the next specialist agent to invoke:\n\n"
    "- 'TransportAgent': For searching flights, intercity buses, trains, or local transportation.\n"
    "- 'AccommodationAgent': For finding hotels, resorts, homestays, or villas.\n"
    "- 'WeatherAgent': For checking weather forecasts, climate info, or packing/clothing advice.\n"
    "- 'SocialReviewAgent': For gathering real user reviews, authentic experiences, and local warnings from TikTok, Threads, or Facebook.\n"
    "- 'BudgetAgent': For currency exchange (VND/USD) and calculating overall trip budgets.\n"
    "- 'ItineraryAgent': When sufficient information is gathered and it is time to generate a comprehensive day-by-day itinerary.\n\n"
    "CRITICAL: You must ensure full bilingual support (Vietnamese and English). Select 'FINISH' only when all user requests have been completely fulfilled and the final response is ready to be delivered."
)

class Router(BaseModel):
    next_node: Literal[
        "TransportAgent", 
        "AccommodationAgent", 
        "WeatherAgent", 
        "SocialReviewAgent", 
        "BudgetAgent", 
        "ItineraryAgent", 
        "FINISH"
    ]

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.0
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
    ("system", "Dựa trên cuộc hội thoại trên, hãy chọn bước xử lý tiếp theo (next_node).")
])

supervisor_chain = prompt | llm.with_structured_output(Router)