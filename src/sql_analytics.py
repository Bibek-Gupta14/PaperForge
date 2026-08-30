import os
from typing import TypedDict, List, Any
from langgraph.graph import StateGraph, START, END
from src.db import execute_sql_query

class SQLState(TypedDict):
    question: str
    schema: str
    sql: str
    error: str
    attempts: int
    rows: List[Any]
    final_answer: str
    status: str

def get_llm():
    """Initializes OpenRouter ChatOpenAI model if a valid non-placeholder OPENROUTER_API_KEY is set."""
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if api_key and not api_key.startswith("your_") and not api_key.startswith("gsk_"):
        model_name = os.getenv("OPENROUTER_MODEL", "nvidia/llama-nemotron-rerank-vl-1b-v2:free")
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model_name=model_name,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.1
        )
    return None

def schema_lookup(state: SQLState) -> SQLState:
    """Paper Listing 5.1: Retrieve schema DDL for query formulation."""
    return {"schema": "CREATE TABLE sales (id INTEGER PRIMARY KEY, amount REAL, region TEXT);"}

def sql_generation(state: SQLState) -> SQLState:
    """Paper Listing 5.1: Generate or repair SQL query using OpenRouter model or fallback."""
    attempts = state.get("attempts", 0) + 1
    llm = get_llm()
    
    if llm:
        from langchain_core.messages import SystemMessage, HumanMessage
        system_prompt = (
            "You are an expert SQL assistant. Given a database schema and a question, return ONLY a valid SQL query. "
            "Do not include markdown code block quotes, explanations, or backticks."
        )
        user_prompt = f"Schema:\n{state.get('schema')}\n\nQuestion: {state.get('question')}"
        if state.get("error"):
            user_prompt += f"\n\nPrevious attempt failed with error: {state.get('error')}. Please fix the query."

        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
        sql = response.content.strip().replace("```sql", "").replace("```", "").strip()
    else:
        # Deterministic Mock Fallback Mode
        err = state.get("error", "")
        if "no such column" in err.lower():
            sql = "SELECT SUM(amount) FROM sales;"
        elif state.get("question") == "Invalid query?" and attempts < 3:
            sql = "DELETE FROM sales;"
        elif attempts > 1 and not state.get("sql"):
            sql = "SELECT SUM(amount) FROM sales;"
        else:
            sql = state.get("sql") or "SELECT SUM(bad_column) FROM sales;"

    return {"sql": sql, "attempts": attempts}

def sql_validation(state: SQLState) -> SQLState:
    """Paper Listing 5.1: Validate SQL syntax."""
    sql = state.get("sql", "")
    if not sql.strip().upper().startswith("SELECT"):
        return {"error": "Syntax Error: Only SELECT queries are permitted.", "status": "invalid"}
    return {"error": "", "status": "validated"}

def query_execution(state: SQLState) -> SQLState:
    """Paper Listing 5.1: Execute query against DB layer (SQLite / MySQL / Postgres)."""
    sql = state.get("sql", "")
    rows, err = execute_sql_query(sql)
    if err:
        return {"rows": [], "error": err, "status": "execution_failed"}
    return {"rows": rows, "error": "", "status": "executed"}

def business_summary(state: SQLState) -> SQLState:
    """Paper Listing 5.1: Summarize query rows into natural language."""
    rows = state.get("rows", [])
    val = rows[0][0] if rows and rows[0] else 0.0
    return {"final_answer": f"Total sales amount across regions is ${val:,.2f}"}

def fail(state: SQLState) -> SQLState:
    """Paper Listing 5.1: Terminal failure node when retries are exhausted."""
    return {"final_answer": f"Failed after {state.get('attempts', 0)} attempts. Last error: {state.get('error')}"}

def route_after_validation(state: SQLState) -> str:
    """Paper Listing 5.1: Route based on validation status."""
    if state.get("status") == "validated":
        return "execute"
    if state.get("attempts", 0) < 3:
        return "retry"
    return "fail"

def route_after_execution(state: SQLState) -> str:
    """Paper Listing 5.1: Route based on database execution outcome."""
    if state.get("status") == "executed":
        return "summarize"
    if state.get("attempts", 0) < 3:
        return "retry"
    return "fail"

def build_sql_graph():
    builder = StateGraph(SQLState)
    builder.add_node("schema_lookup", schema_lookup)
    builder.add_node("sql_generation", sql_generation)
    builder.add_node("sql_validation", sql_validation)
    builder.add_node("query_execution", query_execution)
    builder.add_node("business_summary", business_summary)
    builder.add_node("fail", fail)

    builder.add_edge(START, "schema_lookup")
    builder.add_edge("schema_lookup", "sql_generation")
    builder.add_edge("sql_generation", "sql_validation")
    builder.add_conditional_edges(
        "sql_validation",
        route_after_validation,
        {"execute": "query_execution", "retry": "sql_generation", "fail": "fail"}
    )
    builder.add_conditional_edges(
        "query_execution",
        route_after_execution,
        {"summarize": "business_summary", "retry": "sql_generation", "fail": "fail"}
    )
    builder.add_edge("business_summary", END)
    builder.add_edge("fail", END)

    return builder.compile()
