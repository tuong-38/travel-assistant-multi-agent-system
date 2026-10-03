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

# Model 3.5-Flash cho các Agent chuyên biệt gọi Function/Tool
llm_tools = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Model 3.6-Flash cho Agent tổng hợp Lịch trình & Phân tích Review
llm_reasoning = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Gán tools cho 3.5-flash
transport_agent_llm = llm_tools.bind_tools([search_flights, search_local_transport])
weather_agent_llm = llm_tools.bind_tools([get_current_weather, suggest_clothing])
accommodation_agent_llm = llm_tools.bind_tools([search_accommodations])
budget_agent_llm = llm_tools.bind_tools([convert_currency, calculate_trip_budget])

# Social Review Agent & Itinerary Agent sử dụng 3.6-flash
social_agent_llm = llm_reasoning.bind_tools([search_social_reviews])

itinerary_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert Smart Travel Itinerary Planner supporting Vietnamese and English.

USER CONTEXT (Read carefully and apply strictly):
- User Nationality: {nationality}
- Starting Location / Departure City: {starting_location}
- Planned Departure Date: {travel_date}
- Duration of Trip: {duration_days} days
- Currency: {currency}

INSTRUCTIONS:
1. ALWAYS plan travel logistics starting directly from '{starting_location}' beginning on '{travel_date}' for {duration_days} days. Do NOT ask the user for departure location or dates again.
2. Synthesize transport, weather, accommodations, budget, and social media reviews into a structured day-by-day itinerary.
3. INCLUDE CLICKABLE LINKS & MEDIA: Whenever mentioning places, food, or hotels, include real review links or URLs (TikTok, Threads, YouTube, Google Maps) retrieved by tools. You may also include public image markdown links like ![Image](URL) if available in search results.
4. Format response using clean, beautiful Markdown with appropriate emojis."""),
    MessagesPlaceholder(variable_name="messages")
])

itinerary_agent_llm = itinerary_prompt | llm_reasoning