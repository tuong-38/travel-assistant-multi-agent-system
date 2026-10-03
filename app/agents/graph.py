import os
import asyncio
from typing import Literal
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, START, END

from app.core.state import TravelState
from app.agents.supervisor import supervisor_chain
from app.agents.guardrail import check_input_guardrail
from app.agents.specialists import (
    transport_agent_llm,
    accommodation_agent_llm,
    weather_agent_llm,
    social_agent_llm,
    budget_agent_llm,
    itinerary_agent_llm
)

# --- Nodes với Rate Limit Delay (1s) ---

async def guardrail_node(state: TravelState):
    user_query = state.get("user_query") or (state["messages"][-1].content if state.get("messages") else "")
    guard_result = check_input_guardrail(user_query)
    
    if not guard_result.is_safe:
        return {
            "hitl_status": "BLOCKED",
            "messages": [AIMessage(content=f"⚠️ Request Blocked: {guard_result.reason}")]
        }
    return {"hitl_status": "PASSED"}

async def supervisor_node(state: TravelState):
    if state.get("hitl_status") == "BLOCKED":
        return {"hitl_status": "FINISH"}
    
    await asyncio.sleep(1)  # Nhịp nghỉ tránh vượt Quota API
    result = supervisor_chain.invoke(state)
    return {"hitl_status": result.next_node}

async def transport_node(state: TravelState):
    await asyncio.sleep(1)
    response = transport_agent_llm.invoke(state["messages"])
    return {"messages": [response]}

async def accommodation_node(state: TravelState):
    await asyncio.sleep(1)
    response = accommodation_agent_llm.invoke(state["messages"])
    return {"messages": [response]}

async def weather_node(state: TravelState):
    await asyncio.sleep(1)
    response = weather_agent_llm.invoke(state["messages"])
    return {"messages": [response]}

async def social_review_node(state: TravelState):
    await asyncio.sleep(1)
    response = social_agent_llm.invoke(state["messages"])
    return {"messages": [response]}

async def budget_node(state: TravelState):
    await asyncio.sleep(1)
    response = budget_agent_llm.invoke(state["messages"])
    return {"messages": [response]}

async def itinerary_node(state: TravelState):
    await asyncio.sleep(1)
    response = itinerary_agent_llm.invoke({"messages": state["messages"]})
    return {
        "messages": [response],
        "hitl_status": "WAITING_APPROVAL"
    }

# --- StateGraph Assembly ---

builder = StateGraph(TravelState)

builder.add_node("Guardrail", guardrail_node)
builder.add_node("Supervisor", supervisor_node)
builder.add_node("TransportAgent", transport_node)
builder.add_node("AccommodationAgent", accommodation_node)
builder.add_node("WeatherAgent", weather_node)
builder.add_node("SocialReviewAgent", social_review_node)
builder.add_node("BudgetAgent", budget_node)
builder.add_node("ItineraryAgent", itinerary_node)

builder.add_edge(START, "Guardrail")

def route_guardrail(state: TravelState) -> str:
    if state.get("hitl_status") == "BLOCKED":
        return END
    return "Supervisor"

builder.add_conditional_edges("Guardrail", route_guardrail, {"Supervisor": "Supervisor", END: END})

def route_supervisor(state: TravelState) -> str:
    next_node = state.get("hitl_status")
    if next_node == "FINISH" or not next_node:
        return END
    return next_node

builder.add_conditional_edges(
    "Supervisor",
    route_supervisor,
    {
        "TransportAgent": "TransportAgent",
        "AccommodationAgent": "AccommodationAgent",
        "WeatherAgent": "WeatherAgent",
        "SocialReviewAgent": "SocialReviewAgent",
        "BudgetAgent": "BudgetAgent",
        "ItineraryAgent": "ItineraryAgent",
        END: END
    }
)

for agent in ["TransportAgent", "AccommodationAgent", "WeatherAgent", "SocialReviewAgent", "BudgetAgent"]:
    builder.add_edge(agent, "Supervisor")

builder.add_edge("ItineraryAgent", "Supervisor")

def compile_graph_with_checkpointer(checkpointer):
    return builder.compile(
        checkpointer=checkpointer,
        interrupt_after=["ItineraryAgent"]
    )