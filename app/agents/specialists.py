import os
import sys
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_mcp_adapters.client import MultiServerMcpToolkit

load_dotenv()

# Khởi tạo LLM Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.3
)

# Cấu hình kết nối tới MCP Server qua Stdio Client
mcp_server_script = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mcp_server.py")

async def get_mcp_tools():
    """Khởi tạo MCP Client kết nối đến MCP Server process"""
    toolkit = MultiServerMcpToolkit(
        servers={
            "travel_mcp": {
                "command": sys.executable,
                "args": [mcp_server_script],
                "transport": "stdio",
            }
        }
    )
    # Lấy danh sách toàn bộ tools từ MCP Server
    tools = await toolkit.get_tools()
    return tools

# Prompt chuẩn hóa bằng tiếng Anh hỗ trợ đa ngôn ngữ
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
4. Language Requirement: Respond primarily in Vietnamese if the user asks in Vietnamese. Respond in English if the user asks in English. Automatically format currency in both VND and USD where applicable."""),
    MessagesPlaceholder(variable_name="messages")
])

itinerary_agent_llm = itinerary_prompt | llm