from langgraph.graph import END
from graph.state import State
from config import Config


def tool_call_router(state: State):
    if state["require_fetching"]:
        return "keyword_extraction_node"
    else:
        return "llm_node"
    

def required_tool_output_summarization_router(state: State):
    if len(state["tool_output"]) > 0:
        return "tool_output_summarize_node"
    else:
        return "llm_node"
    

def chat_summary_router(state: State):
    messages = state["messages"][state.get("summarized_till_index", -1) + 1:]
    if len(messages) >= Config.SUMMARIZE_MESSAGE_COUNT + Config.LAST_KEEP_MESSAGE_COUNT:
        return "summarize_chat_node"
    else:
        return END