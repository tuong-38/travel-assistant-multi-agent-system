import streamlit as st
import requests
import uuid
from datetime import date

st.set_page_config(page_title="Multi-Agent Travel Assistant", page_icon="✈️", layout="wide")

API_BASE_URL = "http://localhost:8000/api"

if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{uuid.uuid4().hex[:6]}"
if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"session_{uuid.uuid4().hex[:8]}"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "waiting_hitl" not in st.session_state:
    st.session_state.waiting_hitl = False

# Sidebar: Thu thập ngữ cảnh chi tiết
st.sidebar.title("👤 Tùy Chọn Chuyến Đi")

nationality = st.sidebar.text_input("Quốc tịch / Nationality", value="Việt Nam")
starting_location = st.sidebar.text_input("Điểm xuất phát / Starting Point", value="Hà Nội")

# Ô chọn Ngày khởi hành & Số ngày du lịch
travel_date_val = st.sidebar.date_input("Ngày dự định khởi hành", value=date.today())
duration_days = st.sidebar.number_input("Số ngày du lịch dự kiến", min_value=1, max_value=30, value=3)

language = st.sidebar.selectbox("Ngôn ngữ / Language", ["vi", "en"], format_func=lambda x: "Tiếng Việt" if x == "vi" else "English")
currency = st.sidebar.selectbox("Đơn vị tiền tệ / Currency", ["VND", "USD"])

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Tạo chuyến đi mới", use_container_width=True):
    st.session_state.thread_id = f"session_{uuid.uuid4().hex[:8]}"
    st.session_state.messages = []
    st.session_state.waiting_hitl = False
    st.rerun()

st.title("✈️ Multi-Agent Travel Assistant System")
st.caption("Hệ thống trợ lý du lịch đa đại lý tích hợp Review TikTok/Threads, Vé máy bay, Khách sạn, Thời tiết & Ngân sách.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Nhập địa điểm bạn muốn tới (VD: Lập lịch trình đi Đà Nẵng)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤖 Các Agents đang phân tích & thu thập dữ liệu review..."):
            try:
                payload = {
                    "user_id": st.session_state.user_id,
                    "thread_id": st.session_state.thread_id,
                    "message": prompt,
                    "language": language,
                    "currency": currency,
                    "nationality": nationality,
                    "starting_location": starting_location,
                    "travel_date": str(travel_date_val),
                    "duration_days": int(duration_days)
                }
                res = requests.post(f"{API_BASE_URL}/chat", json=payload, timeout=90)
                
                if res.status_code == 200:
                    data = res.json()
                    bot_response = data.get("response", "Không nhận được phản hồi.")
                    st.markdown(bot_response)
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})

                    if data.get("hitl_status") == "WAITING_APPROVAL":
                        st.session_state.waiting_hitl = True
                else:
                    st.error(f"Lỗi Backend API: {res.text}")

            except Exception as e:
                st.error(f"Lỗi kết nối Backend API: {str(e)}")

# Khung duyệt HITL
if st.session_state.waiting_hitl:
    st.warning("⚠️ **XÁC NHẬN LỊCH TRÌNH (Human-in-the-Loop)**: Hãy xem xét bản thảo lịch trình trên và chọn thao tác:")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Đồng ý & Chốt Lịch Trình (Approve)", use_container_width=True):
            res = requests.post(
                f"{API_BASE_URL}/hitl/respond",
                json={"user_id": st.session_state.user_id, "thread_id": st.session_state.thread_id, "action": "APPROVED"}
            )
            if res.status_code == 200:
                st.success("🎉 Lịch trình đã được chốt thành công!")
                st.session_state.waiting_hitl = False
                st.rerun()

    with col2:
        feedback = st.text_input("Góp ý chỉnh sửa (nếu có):", placeholder="VD: Đổi giúp tôi sang dạng Resort gần biển...")
        if st.button("❌ Yêu cầu Sửa đổi (Request Changes)", use_container_width=True):
            res = requests.post(
                f"{API_BASE_URL}/hitl/respond",
                json={
                    "user_id": st.session_state.user_id,
                    "thread_id": st.session_state.thread_id,
                    "action": "REJECTED",
                    "feedback": feedback
                }
            )
            if res.status_code == 200:
                st.info("🔄 Yêu cầu sửa đổi đã được gửi lại cho các Agents!")
                st.session_state.waiting_hitl = False
                st.rerun()