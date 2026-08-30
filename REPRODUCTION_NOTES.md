# Ambiguity Audit & Reproduction Notes

- **Paper**: Graph-Based Agentic AI with LangGraph (arXiv:2607.19297)
- **Target Goal**: Extension (Reproduce core recipes + add custom extension/evaluation)

## Ambiguity Table

| Decision / Choice | Paper Status | Evidence / Paper Text | Chosen Baseline Value | Alternatives |
| :--- | :--- | :--- | :--- | :--- |
| **SQL Max Retries** | `UNSPECIFIED` | Section 5.1 includes retry edges but no hard integer limit | `3` | `5`, exponential backoff |
| **SQL Engine** | `UNSPECIFIED` | Uses generic execution node | In-memory SQLite / mock execution | PostgreSQL, DuckDB |
| **Evidence Grading Logic** | `PARTIALLY_SPECIFIED` | Section 5.2 defines document relevancy check | Keyword filter / similarity score threshold | LLM grader model |
| **HITL Checkpointer Backend** | `SPECIFIED` | Section 5.3 explicitly specifies `MemorySaver` | `langgraph.checkpoint.memory.MemorySaver` | `SqliteSaver`, `PostgresSaver` |
