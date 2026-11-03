import json
from decimal import Decimal
from datetime import date, datetime
from sqlalchemy import text
from langchain_core.tools import tool


def make_tools(db, vectorstore=None):
    """Recebe a instância do banco e do vectorstore e retorna a lista de ferramentas."""

    def _json_default(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    @tool(parse_docstring=True)
    def query_sql(sql: str) -> str:
        """Executa uma consulta SQL, somente SELECT, e retorna os resultados.

        Args:
            sql: Comando SQL (apenas SELECT; sem DDL/DML).

        Returns:
            Uma string JSON com chaves:
            - "columns": lista de nomes das colunas
            - "rows": lista de linhas (lista de valores)
            - "rowcount": número de linhas
            - "timestamp": momento da execução (ISO 8601)
        """
        if not db:
            return json.dumps({"error": "Sem conexão com o banco (DATABASE_URL ausente).", "timestamp": datetime.now().isoformat()})
        s = sql.strip().lower()
        forbidden = any(k in s for k in [" insert ", " update ", " delete ", " drop ", " alter ", " truncate ", " create "])
        starts_with_select = s.startswith("select")
        if forbidden or not starts_with_select:
            return json.dumps({"error": "Somente SELECT é permitido pelo agente.", "timestamp": datetime.now().isoformat()})

        try:
            with db._engine.connect() as conn:
                result = conn.execute(text(sql))
                cols = list(result.keys())
                rows = [list(r) for r in result.fetchall()]
            return json.dumps({"columns": cols, "rows": rows, "rowcount": len(rows), "timestamp": datetime.now().isoformat()}, ensure_ascii=False, default=_json_default)
        except Exception as e:
            return json.dumps({"error": str(e), "sql": sql, "timestamp": datetime.now().isoformat()}, ensure_ascii=False)

    @tool(parse_docstring=True)
    def search_store_policies(query: str) -> str:
        """Busca trechos relevantes no documento de políticas da loja via RAG (FAISS).

        Args:
            query: Pergunta ou termo de busca sobre políticas, frete, trocas, garantia, pagamento ou horários da loja.

        Returns:
            Uma string JSON com os trechos encontrados no documento e o timestamp.
        """
        if not vectorstore:
            return json.dumps({"error": "Vectorstore de políticas não inicializado.", "timestamp": datetime.now().isoformat()})

        try:
            docs = vectorstore.similarity_search(query, k=4)
            chunks = [doc.page_content for doc in docs]
            return json.dumps({"query": query, "chunks": chunks, "rowcount": len(chunks), "timestamp": datetime.now().isoformat()}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e), "query": query, "timestamp": datetime.now().isoformat()}, ensure_ascii=False)

    return [query_sql, search_store_policies]
