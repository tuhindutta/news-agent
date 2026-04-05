from typing import List
from langchain_core.messages.base import BaseMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from graph.state import ToolDecide


def format_chat_history(hist:List[BaseMessage]) -> str:
    text = ""
    for msg in hist:
        txt = f"{msg.__class__.__name__}: {msg.content}\n\n"
        text += txt
    text = text.strip()
    return text


# client = MultiServerMCPClient(
#         {
#             "news_and_url_scraping": {
#                 "transport": "http",
#                 "url": "http://localhost:8000/mcp"
#             }
#         }
#     )


# async def get_tools_response(call:ToolDecide) -> str:

#     tools = await client.get_tools()
#     tools_map = {i.name:i for i in tools}
#     tool = tools_map[call.tool_name]
#     args = {list(tool.args.keys())[0] : call.tool_input}

#     res = await tool.ainvoke(args)
#     res = '\n\n'.join([i['text'] for i in res])
    
#     return res


class ToolResponse:

    def __init__(self, MCP_URI:str):
        self.__client = MultiServerMCPClient(
            {
                "news_and_url_scraping": {
                    "transport": "http",
                    "url": MCP_URI
                }
            }
        )

    async def get_tools_response(self, call:ToolDecide) -> str:

        tools = await self.__client.get_tools()
        tools_map = {i.name:i for i in tools}
        tool = tools_map[call.tool_name]
        args = {list(tool.args.keys())[0] : call.tool_input}

        res = await tool.ainvoke(args)
        res = '\n\n'.join([i['text'] for i in res])
        
        return res
    

