import inspect
from tqdm import tqdm
from langchain_core.prompts import PromptTemplate
from graph.state import State
from langgraph.types import StreamWriter
from graph.llms import summary_llm
# from config import Config



async def tool_output_summarize_node(state: State, writer: StreamWriter):

    prompt = PromptTemplate.from_template(
        """
Generate summary of the below tool output data, required for news reporting.
Also retuen found additional sources, URLs with any associated description.
Ignore topics outside of topic of interest.
Keep it compact.

Topic of interest: Science, Technology, Indian Politics, International Conflicts & Geopolitics, Health & Environment, Sports, Culture

Tool output data:    
{outputs}
        """.strip()
    )
    # print(state)

    chain = prompt | summary_llm

    summaries = []
    tool_outputs = state['tool_output']
    for op in tqdm(tool_outputs, desc="Summarizing: "):
        inp = op.input
        otp = op.output

        if otp.strip() != "":
            # text = f"Input:{inp}\nOutput:{otp}\n\nExisting summary:{state.get("tool_output_summary", "None")}".strip()
            summary = await chain.ainvoke({"outputs": otp}, config={"tools": {"tool_choice": "none"}})
            writer(
                {
                    "input": inp,
                    "output": summary.content
                }
            )
            summ = f"""
    Tool query: {inp}
    Tool output: {summary.content}
    """.strip()
            summaries.append(summ)

        else:
            writer(
                {
                    "input": inp,
                    "output": "No output from tool."
                }
            )

    full_summary = '\n\n'.join(summaries)
    # full_summary = chain.invoke({"outputs": '\n'.join(summaries)}).content

    return {
        "tool_output_summary": full_summary,
        "require_fetching": False,
        "run_till": inspect.currentframe().f_code.co_name
    }