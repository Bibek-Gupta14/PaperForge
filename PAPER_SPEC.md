# Paper Implementation Specification (PAPER_SPEC.md)

**Paper**: *Graph-Based Agentic AI with LangGraph: Workflow Pathways for Long-Running Stateful Business Processes*  
**arXiv ID**: [2607.19297](https://arxiv.org/abs/2607.19297)

---

## 1. Central Contribution (Summary)
- Proposes explicit graph-based orchestration over prompt-only loops for stateful enterprise business logic.
- Defines 3 executable recipe patterns:
  1. **SQL Analytics Repair Loop**: Generates, validates, and executes SQL queries with explicit error retry loops.
  2. **Agentic RAG Evidence Gating**: Multi-stage document retrieval, relevance grading, citation verification, and re-retrieval routing.
  3. **HITL Policy Review**: Human-in-the-loop stateful workflow featuring durable checkpoints (`MemorySaver`) and explicit interrupt resume points (`interrupt_before`).

---

## 2. Required Modules & State Specifications

### A. SQL Analytics Repair Loop (`src/sql_analytics.py`)
- **State Schema (`SQLState`)**:
  - `question`: `str` (user natural language prompt)
  - `schema`: `str` (database schema DDLS)
  - `sql`: `str` (generated SQL query)
  - `error`: `str` (validation or execution error message)
  - `attempts`: `int` (current repair attempt counter)
  - `rows`: `List[List[Any]]` (executed query results)
  - `final_answer`: `str` (business summary output)
  - `status`: `str` (`'validated'`, `'executed'`, `'invalid'`, `'failed'`)
- **Nodes**: `schema_lookup`, `sql_generation`, `sql_validation`, `query_execution`, `business_summary`, `fail`
- **Edges**:
  - `START` $\rightarrow$ `schema_lookup` $\rightarrow$ `sql_generation` $\rightarrow$ `sql_validation`
  - Conditional: `sql_validation` $\xrightarrow{\text{validated}}$ `query_execution`, $\xrightarrow{\text{retry}}$ `sql_generation`, $\xrightarrow{\text{fail}}$ `fail`
  - Conditional: `query_execution` $\xrightarrow{\text{executed}}$ `business_summary`, $\xrightarrow{\text{retry}}$ `sql_generation`, $\xrightarrow{\text{fail}}$ `fail`

### B. Agentic RAG Evidence Loop (`src/agentic_rag.py`)
- **State Schema (`RAGState`)**:
  - `question`: `str`
  - `documents`: `List[str]` (raw retrieved chunks)
  - `graded_documents`: `List[str]` (evidence-filtered chunks)
  - `generation`: `str` (synthesized response)
  - `citation_verified`: `bool` (verification check)
  - `retries`: `int`
- **Nodes**: `retrieve`, `grade`, `generate`, `verify`
- **Edges**:
  - `START` $\rightarrow$ `retrieve` $\rightarrow$ `grade`
  - Conditional: `grade` $\xrightarrow{\text{has docs}}$ `generate`, $\xrightarrow{\text{no docs}}$ `retrieve` / `END`
  - Conditional: `verify` $\xrightarrow{\text{verified}}$ `END`, $\xrightarrow{\text{unverified}}$ `generate`

### C. HITL Policy Review (`src/hitl_policy.py`)
- **State Schema (`HITLState`)**:
  - `policy_id`: `str`
  - `content`: `str`
  - `risk_score`: `float`
  - `status`: `str` (`'flagged'`, `'approved'`, `'human_approved'`, `'final_approved'`, `'final_rejected'`)
  - `approval_comment`: `str`
- **Checkpointer**: `MemorySaver` checkpoint backend
- **Interrupt Point**: `interrupt_before=["human_review"]`

---

## 3. Ambiguity & Decisions Audit

| Decision | Paper Status | Section | Chosen Value | Alternatives |
| :--- | :--- | :--- | :--- | :--- |
| Max Repair Attempts | `UNSPECIFIED` | Sec 5.1 | `3` | `5`, unbounded |
| DB Engine | `UNSPECIFIED` | Sec 5.1 | SQLite / Mock | Postgres |
| Evidence Threshold | `PARTIALLY_SPECIFIED` | Sec 5.2 | Keyword / Relevancy score | LLM Judge |
| Checkpointer | `SPECIFIED` | Sec 5.3 | `MemorySaver` | `SqliteSaver` |
