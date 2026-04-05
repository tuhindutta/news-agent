import inspect
from langchain_core.prompts import PromptTemplate
from graph.state import State
from graph.llms import summary_llm
from graph.utils import format_chat_history
from config import Config



# def summarize_chat_node(state:State):
#     messages = state["messages"]
#     if len(messages) > 2:
#         message_to_summarize = messages[:-Config.LAST_KEEP_MESSAGE_COUNT]
#         formatted_message = format_chat_history(message_to_summarize)

#         prompt = PromptTemplate.from_template(
#             """
#             Summarize the conversation history. Keep the URLs' and sources' references intact for future use.
            
#             {chat}
            
#             Existing chat summary:
#             {chat_summary}
#             """
#         )

#         chain = prompt | summary_llm
#         res = chain.invoke({"chat":formatted_message, "chat_summary":state.get("chat_summary", "None")}).content

#         # messages_to_remove = [RemoveMessage(id=m.id) for m in message_to_summarize] 

#         return {
#             "chat_summary": res,
#             "run_till": inspect.currentframe().f_code.co_name
#         }

async def summarize_chat_node(state:State):
    summarized_till_index = state.get("summarized_till_index", -1)
    message_to_summarize = state.get("messages")[summarized_till_index + 1:-Config.LAST_KEEP_MESSAGE_COUNT]
    formatted_message = format_chat_history(message_to_summarize)

    prompt = PromptTemplate.from_template(
        """
        Summarize the conversation history. Keep the URLs' and sources' references intact for future use.
        
        {chat}
        
        Existing chat summary:
        {chat_summary}
        """
    )

    chain = prompt | summary_llm
    res = await chain.ainvoke({"chat":formatted_message, "chat_summary":state.get("chat_summary", "None")})

    # messages_to_remove = [RemoveMessage(id=m.id) for m in message_to_summarize] 

    return {
        "chat_summary": res.content,
        "summarized_till_index": summarized_till_index + len(message_to_summarize),
        "run_till": inspect.currentframe().f_code.co_name
    }