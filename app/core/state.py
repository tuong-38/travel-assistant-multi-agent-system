from typing import Annotated, List, Dict, Any, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class TravelState(TypedDict):
    """
    Cấu trúc Shared State lưu trữ toàn bộ thông tin luồng chạy Multi-Agent
    """
    # 1. Thông tin người dùng & Phân luồng Session (Cần cho Multi-user & Auth)
    user_id: str
    thread_id: str
    language: str        # 'vi' (Mặc định) hoặc 'en'
    currency: str        # 'VND' (Mặc định) hoặc 'USD'
    nationality: Optional[str]        # Quốc tịch (VD: Việt Nam, Mỹ, Nhật)
    starting_location: Optional[str]  # Điểm bắt đầu (VD: Hà Nội, TP.HCM)
    travel_date: Optional[str]        # Ngày dự định khởi hành (VD: '2026-10-15')
    duration_days: Optional[int]      # Số ngày du lịch (VD: 3, 5)
    
    # 2. Input tìm kiếm ban đầu từ người dùng
    user_query: str
    origin_iata: Optional[str]        # Ví dụ: 'HAN', 'SGN'
    destination: Optional[str]        # Ví dụ: 'Đà Nẵng', 'Tokyo'
    trip_constraints: Dict[str, Any]  # Số lượng người, yêu cầu đặc biệt...

    # 3. Kết quả do các Specialist Agents cào & xử lý về
    flight_results: Optional[List[Dict[str, Any]]]
    hotel_results: Optional[List[Dict[str, Any]]]
    weather_info: Optional[Dict[str, Any]]
    budget_analysis: Optional[Dict[str, Any]]
    social_reviews: Optional[List[Dict[str, Any]]]  # Dữ liệu review MXH (TikTok/Threads/FB)

    # 4. Lịch trình tổng hợp & Trạng thái duyệt Human-in-the-Loop (HITL)
    itinerary_plan: Optional[Dict[str, Any]]
    hitl_status: Optional[str]  # 'PASSED', 'WAITING_APPROVAL', 'APPROVED', 'REJECTED', 'CHANGES_REQUESTED', 'BLOCKED'

    # 5. Danh sách tin nhắn trao đổi giữa User & các Agents
    messages: Annotated[List[BaseMessage], add_messages]