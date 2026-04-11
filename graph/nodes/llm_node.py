import inspect
from datetime import datetime
from langchain.messages import AIMessage, SystemMessage
from graph.state import State
from graph.llms import llm
from config import Config




async def llm_node(state: State):

    system_prompt = f"""
You are an experienced journalist.
You are part of an Agentic AI system. The system already has latest news fetching and URL scraping capabilities.
You will receive relevant tool output to answer from for each user's query.
Present the news topics to user based on the provided real-time trusted context and user query.
Always give reference, citations, URLs and sources along with the news.
Always suggest potential further actions and/or available (provided) URLs to scrape to assist, guide, and encourage the user for further queries.
Do not fabricate any news, sources, URLs. Stick with the provided context strictly.
Date: {datetime.now().strftime("%d-%b-%Y")}

Context (tool output):
{state.get("tool_output_summary", "None")}

Previous chat history:
{state.get("chat_summary", "None")}
""".strip()  
    query = [SystemMessage(system_prompt)]
    query.extend(state.get("messages")[state.get("summarized_till_index", -1) + 1:])
    
    # print(state)

    response = await llm.ainvoke(query, config={"tools": {"tool_choice": "none"}})

    # print(f"{inspect.currentframe().f_code.co_name}:{response}\n\n\n")

    messages = {
        "messages" : [AIMessage(response.content)],
        "llm_input_prompt": query,
        "run_till": inspect.currentframe().f_code.co_name
    }
    return messages