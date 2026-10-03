import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.mcp_tools.transport_tool import search_flights, search_local_transport
from app.mcp_tools.weather_tool import get_current_weather, suggest_clothing
from app.mcp_tools.accommodation_tool import search_accommodations
from app.mcp_tools.social_review_tool import search_social_reviews
from app.mcp_tools.budget_tool import convert_currency, calculate_trip_budget

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Gán Tools trực tiếp vào LLM
transport_agent_llm = llm.bind_tools([search_flights, search_local_transport])
weather_agent_llm = llm.bind_tools([get_current_weather, suggest_clothing])
accommodation_agent_llm = llm.bind_tools([search_accommodations])
social_agent_llm = llm.bind_tools([search_social_reviews])
budget_agent_llm = llm.bind_tools([convert_currency, calculate_trip_budget])

itinerary_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert Smart Travel Itinerary Planner supporting Vietnamese and English natively.
Synthesize all collected data (transport, hotel, weather, social reviews, budget) into a clear day-by-day itinerary."""),
    MessagesPlaceholder(variable_name="messages")
])

itinerary_agent_llm = itinerary_prompt | llm