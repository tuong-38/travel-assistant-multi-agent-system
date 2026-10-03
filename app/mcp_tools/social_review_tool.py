import os
from typing import Dict, Any, Optional
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

@tool
def search_social_reviews(location_or_place: str, platform: Optional[str] = "all") -> Dict[str, Any]:
    """
    Thu thập các bài viết review, trải nghiệm thực tế từ người dùng trên TikTok, Threads, Facebook Groups hoặc Reddit.
    Args:
        location_or_place: Tên địa danh, nhà hàng, khách sạn (ví dụ: 'Phố cổ Hà Nội', 'Quán ốc Đào', 'Bánh mì Phượng')
        platform: Nền tảng muốn tập trung ('tiktok', 'threads', 'facebook', hoặc 'all')
    """
    # Xây dựng Query tìm kiếm nâng cao chỉ định trang web
    if platform == "tiktok":
        query = f'site:tiktok.com "{location_or_place}" review trải nghiệm bẫy du lịch'
    elif platform == "threads":
        query = f'site:threads.net "{location_or_place}" review phốt kinh nghiệm'
    elif platform == "facebook":
        query = f'site:facebook.com/groups "{location_or_place}" review ăn uống du lịch'
    else:
        query = f'(site:tiktok.com OR site:threads.net OR site:facebook.com/groups) "{location_or_place}" review trải nghiệm thực tế'

    if not TAVILY_API_KEY or TAVILY_API_KEY == "tvly-...":
        # Mock data review MXH chân thực
        return {
            "status": "success",
            "source": "mock_data",
            "target": location_or_place,
            "reviews": [
                {
                    "platform": "TikTok",
                    "content": f"Review {location_or_place}: Đi tầm 5h chiều siêu đông, xếp hàng 30p mới có bàn. Đồ ăn tạm ổn nhưng sống ảo view hoàng hôn siêu đẹp nha mọi người!",
                    "url": "https://tiktok.com/@example_review1"
                },
                {
                    "platform": "Threads",
                    "content": f"Mọi người đi {location_or_place} nhớ né gửi xe ngõ bên cạnh ra nha, bị chặt chém 30k/xe đó. Nên gửi ở bãi xe chính chủ của phường.",
                    "url": "https://threads.net/@example_user2"
                }
            ]
        }

    try:
        search_tool = TavilySearchResults(max_results=6, tavily_api_key=TAVILY_API_KEY)
        raw_results = search_tool.invoke({"query": query})
        
        parsed_reviews = []
        if isinstance(raw_results, list):
            for item in raw_results:
                parsed_reviews.append({
                    "title": item.get("title", "Bài viết review MXH"),
                    "snippet": item.get("content", "N/A"),
                    "url": item.get("url", "#")
                })

        return {
            "status": "success",
            "target": location_or_place,
            "search_query": query,
            "reviews": parsed_reviews
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Lỗi khi cào dữ liệu review MXH: {str(e)}"
        }