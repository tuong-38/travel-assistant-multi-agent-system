import os
import requests
from typing import Dict, Any, Optional
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

WEATHERSTACK_API_KEY = os.getenv("WEATHERSTACK_API_KEY") or os.getenv("OPENWEATHER_API_KEY")

@tool
def get_current_weather(location: str) -> Dict[str, Any]:
    """
    Tra cứu thời tiết hiện tại và thông số khí hậu của một địa điểm du lịch.
    Args:
        location: Tên thành phố/địa danh (ví dụ: 'Hà Nội', 'Đà Lạt', 'Phú Quốc', 'Tokyo')
    """
    if not WEATHERSTACK_API_KEY:
        # Mock data nếu chưa cấu hình Weatherstack API Key
        return {
            "status": "success",
            "source": "mock_data",
            "location": location,
            "temperature": 26,
            "condition": "Nắng nhẹ, thoáng mát",
            "humidity": 70,
            "wind_speed": 12,
            "recommendation": "Thời tiết rất lý tưởng cho các hoạt động tham quan ngoài trời."
        }

    url = "http://api.weatherstack.com/current"
    params = {
        'access_key': WEATHERSTACK_API_KEY,
        'query': location
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if "current" in data:
            current = data["current"]
            location_info = data.get("location", {})
            
            weather_desc = current.get("weather_descriptions", ["N/A"])[0]
            temp = current.get("temperature")
            humidity = current.get("humidity")
            
            return {
                "status": "success",
                "location": f"{location_info.get('name')}, {location_info.get('country')}",
                "temperature": f"{temp}°C",
                "condition": weather_desc,
                "humidity": f"{humidity}%",
                "wind_speed": f"{current.get('wind_speed')} km/h",
                "feels_like": f"{current.get('feelslike')}°C"
            }
        else:
            return {
                "status": "error",
                "message": f"Không tìm thấy dữ liệu thời tiết cho: {location}. Chi tiết: {data.get('error', {}).get('info', 'Unknown error')}"
            }

    except Exception as e:
        return {"status": "error", "message": f"Lỗi kết nối tới Weatherstack API: {str(e)}"}


@tool
def suggest_clothing(temperature_celsius: float, condition: str) -> Dict[str, Any]:
    """
    Đưa ra gợi ý chuẩn bị trang phục và vật dụng cá nhân dựa trên nhiệt độ và thời tiết.
    """
    suggestions = []
    
    if temperature_celsius < 15:
        suggestions.append("Áo khoác dày, khăn quàng cổ, găng tay (thời tiết lạnh/rét).")
    elif 15 <= temperature_celsius < 24:
        suggestions.append("Áo khoác nhẹ, quần dài, trang phục thu đông thoải mái.")
    else:
        suggestions.append("Trang phục thoáng mát, chất liệu thấm hút mồ hôi (cotton/linen).")
        
    cond_lower = condition.lower()
    if "rain" in cond_lower or "shower" in cond_lower or "mưa" in cond_lower:
        suggestions.append("Mang theo ô/dù, áo mưa mỏng và túi chống nước cho thiết bị điện tử.")
    if "sun" in cond_lower or "clear" in cond_lower or "nắng" in cond_lower or temperature_celsius > 28:
        suggestions.append("Kem chống nắng, kính râm, mũ/nón rộng vành.")

    return {
        "status": "success",
        "clothing_advice": suggestions
    }