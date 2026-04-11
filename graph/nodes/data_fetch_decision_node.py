import json
import inspect
from graph.state import State, ToolDecide
from graph.utils import format_chat_history
from config import Config
from graph.llms import summary_llm



async def data_fetch_decision_node(state: State):

    query = f"""
You are a decision-making system.

Your job:
Decide whether an external tool is required.

Rules:
1. If the query requires latest/current information → use "get_latest_news"
2. If the query contains a URL → use "scrape_website"
3. Otherwise → no tool required
4. For complex tasks, you can create multiple JSONs each for a tool in a list.


Return ONLY valid JSONs in list. Do not include explanations, text, or formatting.

Strict format:
[
    {{
      "use_tool": true or false,
      "tool_name": "get_latest_news" | "scrape_website" | null,
      "tool_input": string or null,
      "decision_reason": string (reason for tool use decision)
    }}
]

Available context:
Messages history: {format_chat_history(state.get("messages")[state.get("summarized_till_index", -1) + 1:])}
""".strip()
    # llm_struc_op = llm.with_structured_output(ToolRequirement)
    response = await summary_llm.ainvoke(query)

    # print(f"{inspect.currentframe().f_code.co_name}:{response}\n\n\n")

    res = json.loads(response.content)
    require_fetching = any([i["use_tool"] for i in res])
    
    return {
        "require_fetching": require_fetching,
        "tools_required": [ToolDecide(tool_input=i["tool_input"],
                                      tool_name=i["tool_name"],
                                      decision_reason=i["decision_reason"]
                                     ) for i in res if i["use_tool"]],
        "tool_output": [],
        "tool_output_summary": "",                             
        "run_till": inspect.currentframe().f_code.co_name
    }


