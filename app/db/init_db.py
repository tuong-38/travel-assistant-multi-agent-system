import asyncio
import os
import sys
from dotenv import load_dotenv
import psycopg
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

# Load biến môi trường từ .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# SQL tạo các bảng custom cho ứng dụng
CREATE_CUSTOM_TABLES_SQL = """
-- 1. Bảng lưu thông tin Người dùng
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    secret_key VARCHAR(255) UNIQUE NOT NULL,
    preferred_language VARCHAR(5) DEFAULT 'vi',
    preferred_currency VARCHAR(5) DEFAULT 'VND',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Bảng lưu Lịch sử chuyến đi
CREATE TABLE IF NOT EXISTS trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    thread_id VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'DRAFT',
    summary_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
"""


async def init_database():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL không được tìm thấy trong file .env!")

    print("🔄 Đang kết nối tới Supabase PostgreSQL...")

    # 1. Tạo các bảng Custom (users, trips)
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute(CREATE_CUSTOM_TABLES_SQL)
            await conn.commit()
            print("✅ Đã tạo các bảng Custom ('users', 'trips') thành công!")

    # 2. Khởi tạo và thiết lập các bảng Checkpoint cho LangGraph
    async with AsyncPostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
        await checkpointer.setup()
        print(
            "✅ Đã tự động khởi tạo 4 bảng LangGraph Checkpoint ('checkpoints', 'checkpoint_blobs',...)"
        )

    print("\n🎉 HOÀN THÀNH BƯỚC 1.4: Database đã sẵn sàng 100%!")


if __name__ == "__main__":
    # Sửa lỗi ProactorEventLoop trên hệ điều hành Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(init_database())