import json
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from graph.stream_utils import generate_graph_stream
from contextlib import asynccontextmanager
import asyncio
from graph import Agent
from config import Config


class QueryInput(BaseModel):
    query: str
    user_id: str
    thread_id: str

checkpointer = None
graph = Agent()

@asynccontextmanager
async def lifespan(app: FastAPI):

    global checkpointer
    global graph
    # --- Startup Logic (before yield) ---
    print("🚀 Application starting...")
    
    # checkpointer = Checkpointer(Config.POSTGRES_CHECKPOINTER_URI, Agent())
    # await checkpointer.setup_checkpointer()
    
    async with AsyncPostgresSaver.from_conn_string(Config.POSTGRES_CHECKPOINTER_URI) as chk:
        await chk.setup()
        # checkpointer = chk
        graph = graph.compile(checkpointer=chk)
        yield  # app runs here
    checkpointer = None
    print("🛑 Application shutting down: cleaning up resources...")


app = FastAPI(lifespan=lifespan)


@app.post("/news-agent-async/")
async def ainvoke(query_input: QueryInput):
    return StreamingResponse(
        generate_graph_stream(
            graph,
            query_input.query,
            query_input.user_id,
            query_input.thread_id),
        media_type="application/x-ndjson"
    )


async def stream_test(query_input: QueryInput):
    for i in range(10):
        yield json.dumps({
            "node_name": "test_node",
            "node_output": f"Chunk {i+1} for query: {query_input.query} ; user_id: {query_input.user_id} ; thread_id: {query_input.thread_id}"
        }) + "\n"
        await asyncio.sleep(1)

@app.post("/stream-test/")
async def stream_test_endpoint(query_input: QueryInput):
    return StreamingResponse(
        stream_test(query_input),
        media_type="application/x-ndjson"
    )


