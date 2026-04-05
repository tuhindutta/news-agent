import json
import psycopg
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph.state import CompiledStateGraph
from graph.stream_utils import generate_graph_stream



class Checkpointer:

    def __init__(self, POSTGRES_CHECKPOINTER_URI:str, graph:CompiledStateGraph):
        self.POSTGRES_CHECKPOINTER_URI = POSTGRES_CHECKPOINTER_URI
        self.graph = graph
        

    async def reset_checkpointer(self):
        async with await psycopg.AsyncConnection.connect(self.POSTGRES_CHECKPOINTER_URI) as conn:
            async with conn.cursor() as cur:  # No await here
                await cur.execute("""
                    DROP TABLE IF EXISTS checkpoint_writes CASCADE;
                    DROP TABLE IF EXISTS checkpoint_blobs CASCADE;
                    DROP TABLE IF EXISTS checkpoints CASCADE;
                    DROP TABLE IF EXISTS checkpoint_migrations CASCADE;
                """)
            await conn.commit()
        
        async with AsyncPostgresSaver.from_conn_string(self.POSTGRES_CHECKPOINTER_URI) as checkpointer:
            await checkpointer.setup()
            print("Checkpointer DB reset and re-initiated.")

    async def setup_checkpointer(self):
        async with AsyncPostgresSaver.from_conn_string(self.POSTGRES_CHECKPOINTER_URI) as checkpointer:
            await checkpointer.setup()
            print("Checkpointer DB initiated.")


    async def run_graph(self, query: str, user_id: str, thread_id: str):
        try:
            async with AsyncPostgresSaver.from_conn_string(self.POSTGRES_CHECKPOINTER_URI) as checkpointer:
                # await checkpointer.setup()
                config = {"configurable": {"user_id": user_id, "thread_id": thread_id}}
                inputs = {"messages": [query]}
                graph = self.graph.compile(checkpointer=checkpointer)
                return await graph.ainvoke(inputs, config)
        except Exception as e:
            print(f"{e}")

    async def run_graph_async(self, query: str, user_id: str, thread_id: str):
        try:
            async with AsyncPostgresSaver.from_conn_string(self.POSTGRES_CHECKPOINTER_URI) as checkpointer:
                # await checkpointer.setup()
                graph = self.graph.compile(checkpointer=checkpointer)
                async for i in generate_graph_stream(graph, query, user_id, thread_id):
                    yield json.dumps(i) + "\n"
        except Exception as e:
            error_msg = {
                "node_name": "error",
                "node_output": str(e)
            }
            yield json.dumps(error_msg) + "\n"