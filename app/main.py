import os
import sys
import asyncio
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.agents.graph import compile_graph_with_checkpointer

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI(title="Multi-Agent Travel Assistant API", version="1.0.0")

DATABASE_URL = os.getenv("DATABASE_URL")

def extract_text_from_message(content) -> str:
    """Xử lý bóc tách danh sách block text từ phản hồi của Gemini 3.6"""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                text_parts.append(part.get("text", ""))
            elif isinstance(part, str):
                text_parts.append(part)
        return "\n".join(text_parts)
    return str(content)

class ChatRequest(BaseModel):
    user_id: str
    thread_id: str
    message: str
    language: Optional[str] = "vi"
    currency: Optional[str] = "VND"
    nationality: Optional[str] = "Việt Nam"
    starting_location: Optional[str] = "Hà Nội"
    travel_date: Optional[str] = None
    duration_days: Optional[int] = 3

class HITLResponseRequest(BaseModel):
    user_id: str
    thread_id: str
    action: str  # 'APPROVED' hoặc 'REJECTED'
    feedback: Optional[str] = None

@app.get("/")
def root():
    return {"status": "online", "message": "Multi-Agent Travel Assistant API is running!"}

@app.post("/api/chat")
async def process_chat(req: ChatRequest):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL chưa được cấu hình!")

    try:
        async with AsyncPostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
            graph_app = compile_graph_with_checkpointer(checkpointer)
            config = {"configurable": {"thread_id": req.thread_id}}

            initial_state = {
                "user_id": req.user_id,
                "thread_id": req.thread_id,
                "language": req.language,
                "currency": req.currency,
                "nationality": req.nationality,
                "starting_location": req.starting_location,
                "travel_date": req.travel_date,
                "duration_days": req.duration_days,
                "user_query": req.message,
                "messages": [HumanMessage(content=req.message)]
            }

            final_message = ""
            hitl_status = "COMPLETED"

            async for event in graph_app.astream(initial_state, config):
                for node_name, state_update in event.items():
                    if "messages" in state_update and state_update["messages"]:
                        raw_content = state_update["messages"][-1].content
                        final_message = extract_text_from_message(raw_content)
                    if "hitl_status" in state_update:
                        hitl_status = state_update["hitl_status"]

            return {
                "status": "success",
                "thread_id": req.thread_id,
                "hitl_status": hitl_status,
                "response": final_message
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")

@app.post("/api/hitl/respond")
async def respond_hitl(req: HITLResponseRequest):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL chưa được cấu hình!")

    try:
        async with AsyncPostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
            graph_app = compile_graph_with_checkpointer(checkpointer)
            config = {"configurable": {"thread_id": req.thread_id}}

            if req.action == "APPROVED":
                resume_input = {"hitl_status": "APPROVED"}
            else:
                feedback_msg = req.feedback or "Tôi muốn điều chỉnh lại lịch trình này."
                resume_input = {
                    "hitl_status": "CHANGES_REQUESTED",
                    "messages": [HumanMessage(content=f"Yêu cầu sửa lịch trình: {feedback_msg}")]
                }

            final_message = ""
            async for event in graph_app.astream(resume_input, config):
                for node_name, state_update in event.items():
                    if "messages" in state_update and state_update["messages"]:
                        raw_content = state_update["messages"][-1].content
                        final_message = extract_text_from_message(raw_content)

            return {
                "status": "success",
                "action": req.action,
                "response": final_message or "Đã cập nhật trạng thái lịch trình thành công!"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý HITL: {str(e)}")