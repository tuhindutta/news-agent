from typing_extensions import Annotated, TypedDict
from typing import List, Literal
from pydantic import BaseModel
from langchain_core.messages.base import BaseMessage
from langgraph.graph.message import add_messages


class ToolDecide(BaseModel):
    tool_input: str = None
    tool_name: Literal["get_latest_news", "scrape_website"] = None
    decision_reason: str

class ToolOutput(BaseModel):
    input: str
    output: str

class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    llm_input_prompt: List[BaseMessage]
    require_fetching:bool
    tool_output: List[ToolOutput] = []
    tool_output_summary: str = ''
    tools_required: List[ToolDecide]
    chat_summary: str
    summarized_till_index: int
    run_till: str