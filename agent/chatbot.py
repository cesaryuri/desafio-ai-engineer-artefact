import os
from db.database import get_db
from rag.vectorstore import initialize_rag_system
from agent.llm import build_llm
from agent.tools import make_tools
from agent.graph import build_graph
from prompts.system_prompt import build_system_prompt


# Inicializa banco SQLite, base RAG, prompt com schema e grafo compilado do assistente
def create_chatbot():
    db_url = os.getenv("DATABASE_URL")
    max_steps = int(os.getenv("MAX_AGENT_STEPS", "10"))

    db = get_db(db_url=db_url)
    vectorstore = initialize_rag_system()

    schema_info = db.get_table_info() if db else ""
    system_prompt = build_system_prompt(schema_info=schema_info, max_steps=max_steps)

    tools = make_tools(db, vectorstore)
    llm, model_name = build_llm(tools)
    graph = build_graph(llm, tools, max_tool_turns=max_steps)

    return graph, system_prompt, model_name, max_steps
