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

# Khởi tạo LLM Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.3
)

# 1. Transport Agent
transport_tools = [search_flights, search_local_transport]
transport_agent_llm = llm.bind_tools(transport_tools)

# 2. Weather Agent
weather_tools = [get_current_weather, suggest_clothing]
weather_agent_llm = llm.bind_tools(weather_tools)

# 3. Accommodation Agent
accommodation_tools = [search_accommodations]
accommodation_agent_llm = llm.bind_tools(accommodation_tools)

# 4. Social Review Agent (Tập trung TikTok/Threads)
social_tools = [search_social_reviews]
social_agent_llm = llm.bind_tools(social_tools)

# 5. Budget Agent
budget_tools = [convert_currency, calculate_trip_budget]
budget_agent_llm = llm.bind_tools(budget_tools)

# 6. Itinerary Agent (Tổng hợp lịch trình)
itinerary_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert Smart Travel Itinerary Planner with native support for both Vietnamese and English.

Your task is to synthesize all retrieved and analyzed data provided by specialist agents:
- Transport & Flights (Airlines, intercity buses, trains, local transit)
- Accommodations (Hotels, resorts, homestays)
- Weather Forecasts & Clothing/Packing advice
- Social Media Reviews & Local tips (TikTok, Threads, Facebook)
- Budgeting & Currency conversions (VND and USD)

GUIDELINES:
1. Generate a clear, structured, engaging, and day-by-day travel itinerary.
2. Include specific recommendations for sightseeing, dining, and logistics.
3. Highlight real-world local tips or warnings extracted from social media reviews.
4. Language Requirement: Respond primarily in Vietnamese if the user asks in Vietnamese (use natural, polite Vietnamese). Respond in English if the user asks in English. Automatically format currency in both VND and USD where applicable."""),
    MessagesPlaceholder(variable_name="messages")
])

itinerary_agent_llm = itinerary_prompt | llm