import os
import pytest
from src.sql_analytics import build_sql_graph
from src.agentic_rag import build_rag_graph
from src.hitl_policy import build_hitl_graph
from src.meta_orchestrator import build_meta_graph
from src.db import execute_sql_query

def test_sql_analytics_successful_repair():
    graph = build_sql_graph()
    initial_state = {
        "question": "Total sales?",
        "schema": "",
        "sql": "",
        "error": "",
        "attempts": 0,
        "rows": [],
        "final_answer": "",
        "status": ""
    }
    result = graph.invoke(initial_state)
    assert result["attempts"] in [1, 2]
    assert result["status"] == "executed"
    assert "Total sales amount across regions is $4,000.00" in result["final_answer"]

def test_sql_analytics_max_retries_failure():
    graph = build_sql_graph()
    initial_state = {
        "question": "Invalid query?",
        "schema": "",
        "sql": "DELETE FROM sales;",
        "error": "",
        "attempts": 0,
        "rows": [],
        "final_answer": "",
        "status": ""
    }
    result = graph.invoke(initial_state)
    assert result["attempts"] == 3
    assert "Failed after 3 attempts" in result["final_answer"]

def test_db_layer_abstraction():
    # Test DB abstraction layer executes queries cleanly
    rows, err = execute_sql_query("SELECT SUM(amount) FROM sales;")
    assert err == ""
    assert rows[0][0] == 4000.0

def test_agentic_rag_full_cycle():
    graph = build_rag_graph()
    initial_state = {
        "question": "What was Q3 growth?",
        "documents": [],
        "graded_documents": [],
        "generation": "",
        "citation_verified": False,
        "retries": 0
    }
    result = graph.invoke(initial_state)
    assert result["citation_verified"] is True
    assert "15%" in result["generation"]

def test_hitl_policy_interrupt_and_resume():
    graph = build_hitl_graph()
    config = {"configurable": {"thread_id": "test_thread_1"}}
    initial_state = {
        "policy_id": "POL-101",
        "content": "This contains confidential user data.",
        "risk_score": 0.0,
        "status": "",
        "approval_comment": ""
    }
    graph.invoke(initial_state, config=config)
    current_state = graph.get_state(config)
    assert "human_review" in current_state.next
    assert current_state.values["status"] == "flagged"

    graph.update_state(config, {"status": "human_approved"})
    final_result = graph.invoke(None, config=config)
    assert final_result["status"] == "final_approved"

def test_meta_orchestrator_routing():
    meta = build_meta_graph()
    res_sql = meta.invoke({"query": "What are total sales?", "intent": "", "sql_result": None, "rag_result": None, "policy_result": None, "final_output": ""})
    assert res_sql["intent"] == "analytics"
    assert "Total sales amount" in res_sql["final_output"]

    res_rag = meta.invoke({"query": "Explain revenue growth", "intent": "", "sql_result": None, "rag_result": None, "policy_result": None, "final_output": ""})
    assert res_rag["intent"] == "rag"
    assert "15%" in res_rag["final_output"]
