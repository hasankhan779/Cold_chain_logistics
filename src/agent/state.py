"""
TypedDict State definition for the LangGraph Logistics Agent.
"""
from typing import TypedDict, Annotated, Sequence, Optional, Dict, Any
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    active_shipment_id: Optional[str]
    context_data: Optional[Dict[str, Any]]

