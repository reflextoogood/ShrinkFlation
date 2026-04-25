"""
ShrinkFlation Detective Agent — LangGraph pipeline.

Graph flow:
  START → agent (LLM reasons + picks tools) → tools (execute) → agent → ... → END

The agent autonomously:
1. Searches the DB for the product
2. Fetches quantity + price history
3. Calculates shrinkflation metrics
4. Cross-checks with Open Food Facts
5. Checks brand severity
6. Produces a plain-English verdict
"""
from __future__ import annotations

import os
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from app.agent.tools import AGENT_TOOLS

SYSTEM_PROMPT = """You are the ShrinkFlation Detective — an AI agent that investigates 
shrinkflation (companies secretly reducing product quantities while keeping prices the same).

When given a product name or query, you MUST:
1. Search the database for the product using search_product_in_db
2. If found, get its quantity history using get_quantity_history
3. Get its price history using get_price_history  
4. Calculate all shrinkflation metrics using calculate_shrinkflation_metrics
5. Cross-check with Open Food Facts using search_open_food_facts
6. Check the brand's overall severity using get_brand_severity
7. Write a clear, consumer-friendly verdict

Your verdict must include:
- Whether shrinkflation occurred (yes/no/unclear)
- How much the quantity shrank (e.g. "−36% since 2010")
- The deception gap color (🟢 green / 🟡 yellow / 🔴 red)
- A plain-English explanation a consumer can understand
- A severity rating: MILD / MODERATE / SEVERE

Always cite your sources. Be direct and consumer-focused."""


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def build_agent_graph() -> StateGraph:
    """Build and compile the LangGraph agent."""
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        api_key=os.environ.get("OPENAI_API_KEY"),
    ).bind_tools(AGENT_TOOLS)

    tool_node = ToolNode(AGENT_TOOLS)

    def agent_node(state: AgentState) -> AgentState:
        """LLM reasons and decides which tools to call."""
        messages = state["messages"]
        # Prepend system prompt if first message
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        response = llm.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: AgentState) -> str:
        """Route: if last message has tool calls → run tools, else → end."""
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "tools"
        return END

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    return graph.compile()


# Singleton compiled graph
_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_agent_graph()
    return _graph


async def run_agent(query: str) -> str:
    """
    Run the ShrinkFlation Detective agent on a query.
    Returns the final plain-English verdict.
    """
    graph = get_graph()
    result = await graph.ainvoke({
        "messages": [HumanMessage(content=query)]
    })
    # Return the last AI message content
    for msg in reversed(result["messages"]):
        if hasattr(msg, "content") and msg.content and not getattr(msg, "tool_calls", None):
            return msg.content
    return "Agent could not produce a verdict."
