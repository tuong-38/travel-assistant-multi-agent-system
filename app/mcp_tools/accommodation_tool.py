import os
from typing import Dict, Any, Optional
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

@tool
def search_accommodations(
    destination: str, 
    accommodation_type: Optional[str] = "khách sạn hoặc homestay", 
    budget_range: Optional[str] = "vừa phải"
) -> Dict[str, Any]:
    """
    Tìm kiếm thông tin các nơi lưu trú (Khách sạn, Resort, Homestay, Hostel) phù hợp tại điểm đến.
    Args:
        destination: Tên thành phố/địa điểm (ví dụ: 'Đà Lạt', 'Phú Quốc', 'Hà Giang')
        accommodation_type: Loai nơi lưu trú ('homestay', 'khách sạn 3-5 sao', 'resort', 'villa')
        budget_range: Mức ngân sách ('gương tiết kiệm', 'vừa phải', 'cao cấp/sang trọng')
    """
    query = f"top {accommodation_type} đẹp giá {budget_range} ở {destination} review đánh giá giá phòng"
    
    if not TAVILY_API_KEY or TAVILY_API_KEY == "tvly-...":
        # Mock data nếu chưa cấu hình Tavily Key
        return {
            "status": "success",
            "source": "mock_data",
            "destination": destination,
            "results": [
                {
                    "name": f"{destination} Heritage Homestay",
                    "type": "Homestay",
                    "price_est": "500,000 - 800,000 VND/đêm",
                    "highlights": "Không gian ấm cúng, gần trung tâm, chủ nhà thân thiện."
                },
                {
                    "name": f"Central {destination} Hotel & Spa",
                    "type": "Khách sạn 4 sao",
                    "price_est": "1,200,000 - 1,800,000 VND/đêm",
                    "highlights": "Bao gồm ăn sáng, có bể bơi vô cực, view đẹp."
                }
            ]
        }

    try:
        search_tool = TavilySearchResults(max_results=5, tavily_api_key=TAVILY_API_KEY)
        raw_results = search_tool.invoke({"query": query})
        
        parsed_results = []
        if isinstance(raw_results, list):
            for item in raw_results:
                parsed_results.append({
                    "title": item.get("title", "N/A"),
                    "snippet": item.get("content", "N/A"),
                    "url": item.get("url", "#")
                })
                
        return {
            "status": "success",
            "destination": destination,
            "search_query": query,
            "results": parsed_results
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Lỗi khi tìm kiếm nơi lưu trú qua Tavily: {str(e)}"
        }