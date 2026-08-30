from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

class HITLState(TypedDict):
    policy_id: str
    content: str
    risk_score: float
    status: str
    approval_comment: str

def evaluate_policy(state: HITLState) -> HITLState:
    # Paper Section 5.3: Automated risk scoring
    score = 0.85 if "confidential" in state.get("content", "").lower() else 0.2
    status = "flagged" if score > 0.5 else "approved"
    return {"risk_score": score, "status": status}

def human_review_step(state: HITLState) -> HITLState:
    # Paper Section 5.3: Interrupt checkpoint step
    return state

def finalize_approval(state: HITLState) -> HITLState:
    return {"status": "final_approved"}

def finalize_rejection(state: HITLState) -> HITLState:
    return {"status": "final_rejected"}

def route_policy(state: HITLState) -> str:
    if state.get("status") == "approved":
        return "auto_approve"
    return "human_review"

def route_after_human(state: HITLState) -> str:
    if state.get("status") == "human_approved":
        return "approve"
    return "reject"

def build_hitl_graph(checkpointer=None):
    if checkpointer is None:
        checkpointer = MemorySaver()

    builder = StateGraph(HITLState)
    builder.add_node("evaluate", evaluate_policy)
    builder.add_node("human_review", human_review_step)
    builder.add_node("finalize_approval", finalize_approval)
    builder.add_node("finalize_rejection", finalize_rejection)

    builder.add_edge(START, "evaluate")
    builder.add_conditional_edges(
        "evaluate",
        route_policy,
        {"auto_approve": "finalize_approval", "human_review": "human_review"}
    )
    builder.add_conditional_edges(
        "human_review",
        route_after_human,
        {"approve": "finalize_approval", "reject": "finalize_rejection"}
    )
    builder.add_edge("finalize_approval", END)
    builder.add_edge("finalize_rejection", END)

    return builder.compile(checkpointer=checkpointer, interrupt_before=["human_review"])
