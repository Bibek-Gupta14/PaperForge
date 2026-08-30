"""
Extension Module: Combined Multi-Recipe Meta-Orchestrator
Extends the 3 paper recipes (SQL Analytics, Agentic RAG, HITL Policy) into a unified enterprise meta-graph.
"""
from typing import TypedDict, Optional, Dict, Any
from langgraph.graph import StateGraph, START, END
from src.sql_analytics import build_sql_graph, SQLState
from src.agentic_rag import build_rag_graph, RAGState
from src.hitl_policy import build_hitl_graph, HITLState

class MetaState(TypedDict):
    intent: str  # 'analytics', 'rag', 'policy'
    query: str
    sql_result: Optional[SQLState]
    rag_result: Optional[RAGState]
    policy_result: Optional[HITLState]
    final_output: str

def classify_intent(state: MetaState) -> MetaState:
    query = state.get("query", "").lower()
    if "sql" in query or "sales" in query or "total" in query:
        intent = "analytics"
    elif "policy" in query or "confidential" in query:
        intent = "policy"
    else:
        intent = "rag"
    return {"intent": intent}

def run_sql_subgraph(state: MetaState) -> MetaState:
    graph = build_sql_graph()
    res = graph.invoke({
        "question": state["query"],
        "schema": "",
        "sql": "",
        "error": "",
        "attempts": 0,
        "rows": [],
        "final_answer": "",
        "status": ""
    })
    return {"sql_result": res, "final_output": res.get("final_answer", "")}

def run_rag_subgraph(state: MetaState) -> MetaState:
    graph = build_rag_graph()
    res = graph.invoke({
        "question": state["query"],
        "documents": [],
        "graded_documents": [],
        "generation": "",
        "citation_verified": False,
        "retries": 0
    })
    return {"rag_result": res, "final_output": res.get("generation", "")}

def run_policy_subgraph(state: MetaState) -> MetaState:
    graph = build_hitl_graph()
    res = graph.invoke({
        "policy_id": "META-101",
        "content": state["query"],
        "risk_score": 0.0,
        "status": "",
        "approval_comment": ""
    })
    return {"policy_result": res, "final_output": f"Policy Status: {res.get('status')}"}

def route_meta_intent(state: MetaState) -> str:
    return state.get("intent", "rag")

def build_meta_graph():
    builder = StateGraph(MetaState)
    builder.add_node("classify", classify_intent)
    builder.add_node("sql_subgraph", run_sql_subgraph)
    builder.add_node("rag_subgraph", run_rag_subgraph)
    builder.add_node("policy_subgraph", run_policy_subgraph)

    builder.add_edge(START, "classify")
    builder.add_conditional_edges(
        "classify",
        route_meta_intent,
        {
            "analytics": "sql_subgraph",
            "rag": "rag_subgraph",
            "policy": "policy_subgraph"
        }
    )
    builder.add_edge("sql_subgraph", END)
    builder.add_edge("rag_subgraph", END)
    builder.add_edge("policy_subgraph", END)

    return builder.compile()
