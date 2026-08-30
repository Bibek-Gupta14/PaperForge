import os
from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END

class RAGState(TypedDict):
    question: str
    documents: List[str]
    graded_documents: List[str]
    generation: str
    citation_verified: bool
    retries: int

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
            temperature=0.2
        )
    return None

def retrieve_documents(state: RAGState) -> RAGState:
    """Paper Section 5.2: Retrieve evidence documents."""
    return {"documents": ["Doc 1: Sales grew by 15% in Q3.", "Doc 2: Unrelated content."]}

def grade_documents(state: RAGState) -> RAGState:
    """Paper Section 5.2: Filter for relevant evidence."""
    docs = state.get("documents", [])
    relevant = [d for d in docs if "Sales" in d or "Q3" in d]
    return {"graded_documents": relevant}

def generate_answer(state: RAGState) -> RAGState:
    """Paper Section 5.2: Generate answer using OpenRouter model or fallback."""
    docs = state.get("graded_documents", [])
    llm = get_llm()
    
    if llm and docs:
        from langchain_core.messages import SystemMessage, HumanMessage
        system_prompt = (
            "You are a helpful research assistant. Answer the user question based strictly on the provided documents. "
            "You MUST cite the source document in your response (e.g., 'Based on Doc 1...')."
        )
        user_prompt = f"Context Documents:\n" + "\n".join(docs) + f"\n\nQuestion: {state.get('question')}"
        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
        generation = response.content.strip()
    else:
        # Fallback Mock Mode
        if docs:
            generation = f"Based on {docs[0]}, sales grew by 15%."
        else:
            generation = "Insufficient evidence found."

    return {"generation": generation}

def verify_citations(state: RAGState) -> RAGState:
    """Paper Section 5.2: Verify citation presence in generated answer."""
    gen = state.get("generation", "")
    has_citation = "Based on" in gen or "Doc" in gen
    return {"citation_verified": has_citation}

def route_after_grading(state: RAGState) -> str:
    if state.get("graded_documents"):
        return "generate"
    if state.get("retries", 0) < 2:
        return "re_retrieve"
    return "fail"

def route_after_verification(state: RAGState) -> str:
    if state.get("citation_verified"):
        return "end"
    return "re_generate"

def build_rag_graph():
    builder = StateGraph(RAGState)
    builder.add_node("retrieve", retrieve_documents)
    builder.add_node("grade", grade_documents)
    builder.add_node("generate", generate_answer)
    builder.add_node("verify", verify_citations)

    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "grade")
    builder.add_conditional_edges(
        "grade",
        route_after_grading,
        {"generate": "generate", "re_retrieve": "retrieve", "fail": END}
    )
    builder.add_edge("generate", "verify")
    builder.add_conditional_edges(
        "verify",
        route_after_verification,
        {"end": END, "re_generate": "generate"}
    )

    return builder.compile()
