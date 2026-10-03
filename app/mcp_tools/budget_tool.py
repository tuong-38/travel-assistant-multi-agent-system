import requests
from typing import Dict, Any, Optional
from langchain_core.tools import tool

# Tỷ giá cố định dự phòng (1 USD = 27,000 VND)
FALLBACK_USD_TO_VND = 27000.0

@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> Dict[str, Any]:
    """
    Quy đổi tiền tệ linh hoạt giữa VND và USD (hoặc các ngoại tệ khác).
    Args:
        amount: Số tiền cần quy đổi (ví dụ: 100 hoặc 2700000)
        from_currency: Đơn vị tiền tệ gốc ('VND' hoặc 'USD')
        to_currency: Đơn vị tiền tệ đích ('VND' hoặc 'USD')
    """
    from_curr = from_currency.upper()
    to_curr = to_currency.upper()
    
    if from_curr == to_curr:
        return {"status": "success", "converted_amount": amount, "currency": to_curr}

    try:
        # Gọi API quy đổi miễn phí từ ExchangeRate-API
        url = f"https://open.er-api.com/v6/latest/{from_curr}"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data.get("result") == "success":
            rate = data["rates"].get(to_curr)
            if rate:
                converted = round(amount * rate, 2)
                return {
                    "status": "success",
                    "original_amount": f"{amount:,} {from_curr}",
                    "converted_amount": f"{converted:,} {to_curr}",
                    "exchange_rate": rate
                }
    except Exception:
        pass  # Nếu lỗi mạng thì chuyển sang dùng fallback rate

    # Dùng tỷ giá fallback nếu API lỗi
    if from_curr == "USD" and to_curr == "VND":
        converted = amount * FALLBACK_USD_TO_VND
    elif from_curr == "VND" and to_curr == "USD":
        converted = round(amount / FALLBACK_USD_TO_VND, 2)
    else:
        converted = amount

    return {
        "status": "success",
        "note": "Dùng tỷ giá quy đổi ước tính",
        "original_amount": f"{amount:,} {from_curr}",
        "converted_amount": f"{converted:,} {to_curr}"
    }


@tool
def calculate_trip_budget(
    flight_cost: float, 
    hotel_cost_per_night: float, 
    nights: int, 
    daily_food_and_activities: float, 
    num_people: int = 1
) -> Dict[str, Any]:
    """
    Tính toán chi phí dự trù tổng thể cho chuyến đi dựa trên vé máy bay, khách sạn và ăn uống/vui chơi.
    """
    total_hotel = hotel_cost_per_night * nights
    total_living = daily_food_and_activities * nights * num_people
    total_flights = flight_cost * num_people
    
    grand_total = total_flights + total_hotel + total_living
    
    return {
        "status": "success",
        "summary": {
            "num_people": num_people,
            "nights": nights,
            "flight_total": f"{total_flights:,} VND",
            "hotel_total": f"{total_hotel:,} VND",
            "living_and_activities_total": f"{total_living:,} VND",
            "grand_total_vnd": f"{grand_total:,} VND",
            "grand_total_usd": f"{round(grand_total / FALLBACK_USD_TO_VND, 2):,} USD"
        }
    }