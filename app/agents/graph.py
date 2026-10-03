from typing import Literal
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END

from app.core.state import TravelState
from app.agents.supervisor import supervisor_chain
from app.agents.specialists import (
    transport_agent_llm,
    accommodation_agent_llm,
    weather_agent_llm,
    social_agent_llm,
    budget_agent_llm,
    itinerary_agent_llm
)

# --- Các hàm Node xử lý cho từng Agent ---

def supervisor_node(state: TravelState):
    result = supervisor_chain.invoke(state)
    return {"hitl_status": result.next_node}

def transport_node(state: TravelState):
    response = transport_agent_llm.invoke(state["messages"])
    return {"messages": [response]}

def accommodation_node(state: TravelState):
    response = accommodation_agent_llm.invoke(state["messages"])
    return {"messages": [response]}

def weather_node(state: TravelState):
    response = weather_agent_llm.invoke(state["messages"])
    return {"messages": [response]}

def social_review_node(state: TravelState):
    response = social_agent_llm.invoke(state["messages"])
    return {"messages": [response]}

def budget_node(state: TravelState):
    response = budget_agent_llm.invoke(state["messages"])
    return {"messages": [response]}

def itinerary_node(state: TravelState):
    response = itinerary_agent_llm.invoke({"messages": state["messages"]})
    return {"messages": [response]}

# --- Xây dựng StateGraph ---

builder = StateGraph(TravelState)

# 1. Thêm các Nodes vào Graph
builder.add_node("Supervisor", supervisor_node)
builder.add_node("TransportAgent", transport_node)
builder.add_node("AccommodationAgent", accommodation_node)
builder.add_node("WeatherAgent", weather_node)
builder.add_node("SocialReviewAgent", social_review_node)
builder.add_node("BudgetAgent", budget_node)
builder.add_node("ItineraryAgent", itinerary_node)

# 2. Cấu hình luồng đi (Edges)
builder.add_edge(START, "Supervisor")

# Luồng điều hướng động từ Supervisor
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

# Tất cả các Agent chuyên biệt sau khi xử lý xong đều quay lại Supervisor để quyết định bước tiếp theo
for agent in ["TransportAgent", "AccommodationAgent", "WeatherAgent", "SocialReviewAgent", "BudgetAgent", "ItineraryAgent"]:
    builder.add_edge(agent, "Supervisor")

# Biên dịch Graph không Checkpointer (Dùng để test)
travel_graph = builder.compile()