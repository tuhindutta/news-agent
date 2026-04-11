import ast
import inspect
from datetime import datetime
from typing import List
from pydantic import BaseModel
from langchain_core.prompts import PromptTemplate
from graph.state import State, ToolDecide
from graph.llms import summary_llm



class Keywords(BaseModel):
    keywords: List[str]
    

async def keyword_extraction_node(state: State):

    prompt = PromptTemplate.from_template("""
You are a keyword-extracting agent.
Extract at most 3 most important keywords, phrases, group of words to maximize search results from a keyword based search engine for the following query.
It must me like a topic, not a question. It should be concise and to the point. like "Russia Ukraine Conflict" instead of "Russia-Ukraine war latest developments 2026".
Return ONLY valid LIST of STRINGs. Do not include explanations, text, or formatting.
Date: {date}

Strict format:
[
    "keyword1 to search", "keyword2 to serach"
]

Query: {query}
    """.strip())
    # print(state)
    # llm_struc_op = llm.with_structured_output(Keywords)
    chain = prompt | summary_llm
    fragmented = []
    for call in state["tools_required"]:
        if call.tool_name == "scrape_website":
            fragmented.append(call)
        elif call.tool_name == "get_latest_news":
            inputs = await chain.ainvoke({"date":datetime.now().strftime("%d-%b-%Y"), "query":call.tool_input})
            for inp in ast.literal_eval(inputs.content):
                new_call = ToolDecide(
                    tool_input=inp,
                    tool_name=call.tool_name,
                    decision_reason=call.decision_reason
                )
                fragmented.append(new_call)

    # print(f"{inspect.currentframe().f_code.co_name}:{fragmented}\n\n\n")
    return {
        "tools_required": fragmented,
        "run_till": inspect.currentframe().f_code.co_name
    }