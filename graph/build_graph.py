from langgraph.graph import StateGraph, START, END
from graph.nodes import *
from graph.routers import *


def build_graph():
    graph = StateGraph(State)
    
    graph = graph.add_node("llm_node", llm_node)
    graph = graph.add_node("data_fetch_decision_node", data_fetch_decision_node)
    graph = graph.add_node("tools_node", tools_node)
    graph = graph.add_node("keyword_extraction_node", keyword_extraction_node)
    graph = graph.add_node("tool_output_summarize_node", tool_output_summarize_node)
    graph = graph.add_node("summarize_chat_node", summarize_chat_node)
    
    graph = graph.add_edge(START, "data_fetch_decision_node")
    
    graph = graph.add_conditional_edges(
        "data_fetch_decision_node",
        tool_call_router,
        {
            "keyword_extraction_node": "keyword_extraction_node",
            "llm_node": "llm_node"
        }
    )
    graph = graph.add_edge("keyword_extraction_node", "tools_node")
    # graph = graph.add_edge("tools_node", "summarize_node")
    graph = graph.add_conditional_edges(
        "tools_node",
        required_tool_output_summarization_router,
        {
            "tool_output_summarize_node": "tool_output_summarize_node",
            "llm_node": "llm_node"
        }
   )
    graph = graph.add_edge("tool_output_summarize_node", "llm_node")
    graph = graph.add_conditional_edges(
        "llm_node",
        chat_summary_router,
        {
            "summarize_chat_node": "summarize_chat_node",
            END: END
        }
    )
    graph.add_edge("summarize_chat_node", END)

    return graph

# graph = graph.add_edge("data_fetch_decision_node", "keyword_extraction_node")
# graph = graph.add_edge("keyword_extraction_node", END)




