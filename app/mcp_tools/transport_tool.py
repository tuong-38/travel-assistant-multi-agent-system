import os
import requests
import airportsdata
from typing import Optional, Dict, Any
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
DEFAULT_ORIGIN_IATA = os.getenv("DEFAULT_ORIGIN_IATA", "HAN")

# Tải dữ liệu sân bay IATA
airports = airportsdata.load('IATA')

def get_iata_code(location_name: str) -> Optional[str]:
    """Hàm hỗ trợ tìm mã IATA từ tên thành phố/sân bay"""
    location_clean = location_name.strip().upper()
    
    # Map nhanh một số sân bay phổ biến tại Việt Nam
    vn_airports = {
        "HÀ NỘI": "HAN", "HA NOI": "HAN", "NỘI BÀI": "HAN",
        "HỒ CHÍ MINH": "SGN", "HO CHI MINH": "SGN", "SÀI GÒN": "SGN", "TÂN SƠN NHẤT": "SGN",
        "ĐÀ NẴNG": "DAD", "DA NANG": "DAD",
        "NHA TRANG": "CXR", "CAM RANH": "CXR",
        "PHÚ QUỐC": "PQC", "PHU QUOC": "PQC",
        "ĐÀ LẠT": "DLI", "DA LAT": "DLI",
        "HẢI PHÒNG": "HPH", "HAI PHONG": "HPH",
        "HUẾ": "HUI", "HUE": "HUI"
    }
    
    if location_clean in vn_airports:
        return vn_airports[location_clean]
        
    for code, data in airports.items():
        if location_clean in data['city'].upper() or location_clean in data['name'].upper():
            return code
            
    return None

@tool
def search_flights(origin: str, destination: str, flight_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Tra cứu thông tin các chuyến bay giữa 2 địa điểm.
    Args:
        origin: Tên thành phố/sân bay đi (ví dụ: 'Hà Nội' hoặc 'HAN')
        destination: Tên thành phố/sân bay đến (ví dụ: 'Đà Nẵng' hoặc 'DAD')
        flight_date: Ngày bay dạng YYYY-MM-DD (Tùy chọn)
    """
    dep_iata = get_iata_code(origin) or DEFAULT_ORIGIN_IATA
    arr_iata = get_iata_code(destination)
    
    if not arr_iata:
        return {
            "status": "error",
            "message": f"Không tìm thấy mã sân bay IATA phù hợp cho điểm đến: {destination}"
        }
        
    if not AVIATIONSTACK_API_KEY:
        # Dummy data nếu chưa điền API Key để test luồng
        return {
            "status": "success",
            "source": "mock_data",
            "flights": [
                {"airline": "Vietnam Airlines", "flight_number": "VN123", "dep": dep_iata, "arr": arr_iata, "price_est": "1,500,000 VND"},
                {"airline": "VietJet Air", "flight_number": "VJ456", "dep": dep_iata, "arr": arr_iata, "price_est": "950,000 VND"}
            ]
        }

    url = "http://api.aviationstack.com/v1/flights"
    params = {
        'access_key': AVIATIONSTACK_API_KEY,
        'dep_iata': dep_iata,
        'arr_iata': arr_iata,
        'limit': 5
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "data" in data and len(data["data"]) > 0:
            flights = []
            for item in data["data"]:
                flights.append({
                    "airline": item.get("airline", {}).get("name", "N/A"),
                    "flight_number": item.get("flight", {}).get("iata", "N/A"),
                    "departure_time": item.get("departure", {}).get("scheduled", "N/A"),
                    "arrival_time": item.get("arrival", {}).get("scheduled", "N/A"),
                    "status": item.get("flight_status", "scheduled")
                })
            return {"status": "success", "origin": dep_iata, "destination": arr_iata, "flights": flights}
        else:
            return {"status": "success", "message": "Không tìm thấy chuyến bay trực tiếp nào trong thời gian này.", "flights": []}
            
    except Exception as e:
        return {"status": "error", "message": f"Lỗi khi gọi AviationStack API: {str(e)}"}

@tool
def search_local_transport(origin: str, destination: str) -> Dict[str, Any]:
    """
    Gợi ý các phương tiện di chuyển đường bộ nội địa (Xe khách, Tàu hỏa, Taxi/Grab).
    """
    return {
        "status": "success",
        "route": f"{origin} ➔ {destination}",
        "options": [
            {"type": "Tàu hỏa (Đường sắt VN)", "duration": "Tùy tuyến", "note": "Phù hợp ngắm cảnh, giá hợp lý"},
            {"type": "Xe khách giường nằm / Limousine", "duration": "Linh hoạt", "note": "Phổ biến, đưa đón tận nơi"},
            {"type": "Grab / Taxi dịch vụ", "duration": "Theo chặng", "note": "Thích hợp di chuyển chặng ngắn hoặc đi nhóm"}
        ]
    }