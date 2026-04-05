from langchain_openai import ChatOpenAI
# from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()


# general_llm = ChatGroq(
#             model='openai/gpt-oss-120b',
#             temperature=0.2,
#             max_tokens=None,
#             reasoning_format="parsed",
#             timeout=None,
#             max_retries=2,
#         )

llm = ChatOpenAI(
            model='gpt-5',
            temperature=0.3
        )

summary_llm = ChatOpenAI(
            model="gpt-5-nano",
            temperature=0
        )