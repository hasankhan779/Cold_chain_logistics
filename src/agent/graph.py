"""
LangGraph ReAct agent orchestration using Anthropic Claude.
Agent is cached so it is only compiled once per session for instant responses.
"""
from functools import lru_cache
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage

from src.config.settings import settings
from src.agent.state import AgentState
from src.agent.prompts import LOGISTICS_AGENT_SYSTEM_PROMPT
from src.agent.tools import AGENT_TOOLS

@lru_cache(maxsize=1)
def get_compiled_agent():
    """Compiles the LangGraph agent once and caches it in memory."""
    llm = ChatAnthropic(
        model_name=settings.ANTHROPIC_MODEL,
        anthropic_api_key=settings.ANTHROPIC_API_KEY,
        temperature=0.1
    ).bind_tools(AGENT_TOOLS)

    def call_model(state: AgentState):
        messages = [SystemMessage(content=LOGISTICS_AGENT_SYSTEM_PROMPT)] + list(state["messages"])
        response = llm.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: AgentState):
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    tool_node = ToolNode(AGENT_TOOLS)

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")

    return workflow.compile()

def create_agent():
    return get_compiled_agent()

def create_agent():
    return get_compiled_agent()

