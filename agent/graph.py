from typing import Literal, Annotated, TypedDict
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def build_graph(llm, tools: list, max_tool_turns: int):

    tool_node = ToolNode(tools)

    def agent_node(state: AgentState):
        msgs = state["messages"]
        resp = llm.invoke(msgs, config=RunnableConfig())
        print(f"usage_metadata={resp.usage_metadata}")
        return {"messages": [resp]}

    def finalize_node(state: AgentState):
        msgs = list(state["messages"])
        last = msgs[-1]

        # Se a última AIMessage ainda tem tool_calls não respondidas
        # (fomos direto para "finalize" sem passar pelo tool_node),
        # feche cada tool_call_id com uma ToolMessage antes de continuar.
        pendentes = []
        if isinstance(last, AIMessage) and last.tool_calls:
            for call in last.tool_calls:
                pendentes.append(
                    ToolMessage(
                        content="Execução não realizada: limite máximo de iterações do agente foi atingido antes desta chamada ser processada.",
                        tool_call_id=call["id"],
                    )
                )

        aviso = HumanMessage(
            "Limite de consultas atingido. Não chame mais nenhuma ferramenta "
            "e escreva agora a resposta final com base nos dados já coletados."
        )

        resp = llm.invoke(msgs + pendentes + [aviso], config=RunnableConfig())
        print(f"usage_metadata={resp.usage_metadata}")
        return {"messages": pendentes + [resp]}

    def should_continue(state: AgentState) -> Literal["tools", "finalize", "__end__"]:
        last = state["messages"][-1]
        if isinstance(last, AIMessage) and last.tool_calls:
            msgs_turno_atual = []
            for m in reversed(state["messages"]):
                if isinstance(m, HumanMessage):
                    break
                msgs_turno_atual.append(m)

            qtd_chamadas = sum(len(m.tool_calls) for m in msgs_turno_atual if isinstance(m, AIMessage) and m.tool_calls)
            if qtd_chamadas >= max_tool_turns:
                return "finalize"
            return "tools"
        return "__end__"

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.add_node("finalize", finalize_node)
    graph.add_edge("tools", "agent")
    graph.add_edge("finalize", END)
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", "finalize": "finalize", "__end__": END})
    graph.set_entry_point("agent")

    return graph.compile()
