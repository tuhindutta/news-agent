import json
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager

import asyncio
from graph import Agent
from checkpointer import Checkpointer
from config import Config


class QueryInput(BaseModel):
    query: str
    user_id: str
    thread_id: str

checkpointer = None

@asynccontextmanager
async def lifespan(app: FastAPI):

    global checkpointer
    # --- Startup Logic (before yield) ---
    print("🚀 Application starting...")
    
    checkpointer = Checkpointer(Config.POSTGRES_CHECKPOINTER_URI, Agent())
    await checkpointer.setup_checkpointer()
    # async def agent_invoke(query: str, user_id: str, thread_id: str):
    #     response = (query, user_id, thread_id)
    #     return response
    
    yield # <-- Application starts running and handling requests here
    
    # --- Shutdown Logic (after yield) ---
    print("🛑 Application shutting down: cleaning up resources...")


app = FastAPI(lifespan=lifespan)


@app.post("/news-agent/")
async def invoke(query_input: QueryInput):
    response = await checkpointer.run_graph(query_input.query, query_input.user_id, query_input.thread_id)
    return {"state": response}


@app.post("/news-agent-async/")
async def ainvoke(query_input: QueryInput):
    return StreamingResponse(
        checkpointer.run_graph_async(
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


@app.post("/reset-checkpointer/")
async def reset():
    await checkpointer.reset_checkpointer()
    return {"RESULT": "Checkpointer DB reset and re-initialized."}


