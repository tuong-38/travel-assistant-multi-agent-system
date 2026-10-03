import sys
import asyncio
from mcp.server.fastmcp import FastMCP

# Import các hàm xử lý cốt lõi từ phase 2
from app.mcp_tools.transport_tool import search_flights, search_local_transport
from app.mcp_tools.weather_tool import get_current_weather, suggest_clothing
from app.mcp_tools.accommodation_tool import search_accommodations
from app.mcp_tools.social_review_tool import search_social_reviews
from app.mcp_tools.budget_tool import convert_currency, calculate_trip_budget

# 1. Khởi tạo MCP Server với tên 'TravelServicesMCP'
mcp = FastMCP("TravelServicesMCP")

# 2. Đăng ký các công cụ (Tools) vào MCP Server
@mcp.tool()
def flight_search(origin: str, destination: str, flight_date: str = None) -> dict:
    """Tra cứu chuyến bay giữa 2 địa điểm."""
    return search_flights.invoke({"origin": origin, "destination": destination, "flight_date": flight_date})

@mcp.tool()
def local_transport_search(origin: str, destination: str) -> dict:
    """Gợi ý xe khách, tàu hỏa, taxi nội địa."""
    return search_local_transport.invoke({"origin": origin, "destination": destination})

@mcp.tool()
def weather_forecast(location: str) -> dict:
    """Tra cứu thời tiết thực tế tại điểm đến."""
    return get_current_weather.invoke({"location": location})

@mcp.tool()
def clothing_advice(temperature_celsius: float, condition: str) -> dict:
    """Tư vấn trang phục dựa trên thời tiết."""
    return suggest_clothing.invoke({"temperature_celsius": temperature_celsius, "condition": condition})

@mcp.tool()
def accommodation_search(destination: str, accommodation_type: str = "khách sạn", budget_range: str = "vừa phải") -> dict:
    """Tìm kiếm khách sạn, resort, homestay."""
    return search_accommodations.invoke({"destination": destination, "accommodation_type": accommodation_type, "budget_range": budget_range})

@mcp.tool()
def social_media_review_search(location_or_place: str, platform: str = "all") -> dict:
    """Cào review chân thực từ TikTok, Threads, Facebook Groups."""
    return search_social_reviews.invoke({"location_or_place": location_or_place, "platform": platform})

@mcp.tool()
def currency_conversion(amount: float, from_currency: str, to_currency: str) -> dict:
    """Quy đổi tiền tệ VND / USD."""
    return convert_currency.invoke({"amount": amount, "from_currency": from_currency, "to_currency": to_currency})

@mcp.tool()
def trip_budget_calculation(flight_cost: float, hotel_cost_per_night: float, nights: int, daily_food_and_activities: float, num_people: int = 1) -> dict:
    """Tính toán tổng chi phí dự trù cho chuyến đi."""
    return calculate_trip_budget.invoke({
        "flight_cost": flight_cost,
        "hotel_cost_per_night": hotel_cost_per_night,
        "nights": nights,
        "daily_food_and_activities": daily_food_and_activities,
        "num_people": num_people
    })

# 3. Chạy MCP Server qua giao thức Stdio
if __name__ == "__main__":
    mcp.run(transport="stdio")