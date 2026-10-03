import os
from typing import Literal
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

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

system_prompt = (
    "You are the Supervisor (Router & Coordinator) of a Multi-Agent Travel System.\n"
    "Based on the conversation history, analyze the last agent output and decide the NEXT step:\n"
    "- 'TransportAgent': For searching flights, intercity buses, trains, or local transit.\n"
    "- 'AccommodationAgent': For finding hotels, resorts, homestays, or villas.\n"
    "- 'WeatherAgent': For checking weather forecasts or clothing advice.\n"
    "- 'SocialReviewAgent': For gathering reviews from TikTok, Threads, or Facebook.\n"
    "- 'BudgetAgent': For currency exchange (VND/USD) and trip budget calculations.\n"
    "- 'ItineraryAgent': When sufficient information is gathered and it is time to generate a full day-by-day itinerary.\n"
    "- 'FINISH': Only when the request is fully completed."
)

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
    ("human", "Based on the dialogue above, who should act next? Respond with next_node.")
])

supervisor_chain = prompt | llm.with_structured_output(Router)