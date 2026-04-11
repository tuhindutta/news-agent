
import json
from graph.state import ToolDecide
from langgraph.graph.state import CompiledStateGraph


def tool_decision_formatting(tool:ToolDecide) -> str:
    return f"""
    {{
        Tool Name: {tool.tool_name}
        Tool Input: {tool.tool_input}
        Reason for use: {tool.decision_reason}
    }}"""

def data_fetch_decision_node_stream(state):
    if state.get("require_fetching"):
        tools_required = state.get("tools_required")
        tools = "\n"
        if len(tools_required) > 0:
            for tool in tools_required:
                tools += tool_decision_formatting(tool) + "\n"
        tools = "Following tools are required:\n\n    "+tools.strip() if tools else " None"
        return tools

    else:
        return "No tools required."
    
def keyword_extraction_node_stream(state):
    tools_required = state.get("tools_required")
    tools = []
    if len(tools_required) > 0:
        for tool in tools_required:
            if tool.tool_name == "get_latest_news":
                tools.append(tool.tool_input)
    keywords = "Following keywords will be searched for latest news:"
    keywords += "\n\n"+", ".join(tools).strip() if len(tools) > 0 else " None"
    return keywords

def llm_node_stream(state):
    msg = state.get("messages")[-1].content
    return msg.strip()


stream_map = {
    "data_fetch_decision_node": data_fetch_decision_node_stream,
    "keyword_extraction_node": keyword_extraction_node_stream,
    "llm_node": llm_node_stream
}


async def generate_graph_stream(graph: CompiledStateGraph, user_input: str, user_id: str, theread_id: str):
    """Async generator to wrap LangGraph stream."""
    inputs = {"messages": user_input}
    config = {"configurable": {"user_id": user_id, "thread_id": theread_id}}
    async for chunk in graph.astream(
        inputs, config,
        stream_mode=["updates", "custom"]
    ):
        mode = chunk[0]
        contents = chunk[1]
        if mode == "updates":
            for node_name, response in contents.items():
                # last_node = state.get("run_till")
                fn = stream_map.get(node_name)
                if fn is not None:
                    stream_output = fn(response)
                    output = {
                        "node_name": node_name,
                        "node_output": stream_output
                    }
                    output = json.dumps(output) + "\n"
                    yield output
        elif mode == "custom":
            inp = contents.get("input")
            otp = contents.get("output")
            text = f"""
Query: {inp}

Output: {otp}
            """.strip()
            output = {
                "node_name": "tool_output_summarize_node",
                "node_output": text
            }
            output = json.dumps(output) + "\n"
            yield output