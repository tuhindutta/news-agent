import inspect
from graph.state import State, ToolOutput
from graph.utils import ToolResponse
from config import Config



async def tools_node(state: State):
    
    messages = []

    tool_res = ToolResponse(Config.MCP_URI)
    # tool_res = ToolResponse('http://localhost:8000/mcp')

    for call in state["tools_required"]:
        msg = await tool_res.get_tools_response(call)
        messages.append(ToolOutput(input=call.tool_input, output=msg))
            
    # state["messages"].extend(messages)
    # print(state)
    
    return {
        "tool_output": messages,
        "run_till": inspect.currentframe().f_code.co_name
    }