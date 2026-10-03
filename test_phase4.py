import asyncio
import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.agents.graph import compile_graph_with_checkpointer

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def run_test():
    print("🔄 Đang kết nối Supabase Postgres Checkpointer...")
    async with AsyncPostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
        app = compile_graph_with_checkpointer(checkpointer)

        config = {"configurable": {"thread_id": "test_session_user_2026"}}

        initial_state = {
            "user_id": "user_2026",
            "thread_id": "test_session_user_2026",
            "language": "vi",
            "currency": "VND",
            "user_query": "Tôi muốn lên kế hoạch đi du lịch Đà Nẵng 3 ngày 2 đêm từ Hà Nội",
            "messages": [HumanMessage(content="Tôi muốn lên kế hoạch đi du lịch Đà Nẵng 3 ngày 2 đêm từ Hà Nội")]
        }

        print("🚀 Đang khởi chạy luồng Multi-Agent...")
        async for event in app.astream(initial_state, config):
            for node_name, state_update in event.items():
                print(f"📍 [Node Hoàn Thành]: {node_name}")
                if "messages" in state_update and state_update["messages"]:
                    last_msg = state_update["messages"][-1]
                    print(f"   💬 Phản hồi: {last_msg.content[:120]}...")

        print("\n🎉 HOÀN THÀNH KIỂM THỬ PHASE 4!")

if __name__ == "__main__":
    # ĐẶT DÒNG NÀY TRƯỚC KHI GỌI asyncio.run()
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(run_test())