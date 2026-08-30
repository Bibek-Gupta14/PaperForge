# Research Reproduction Rules

1. `PAPER_SPEC.md` is the implementation contract for this repository.
2. The research paper (*Graph-Based Agentic AI with LangGraph*, arXiv:2607.19297) is the ultimate source of truth.
3. Never silently invent a hyperparameter, routing threshold, or state field without explicit documentation.
4. Classify and mark every design choice in `REPRODUCTION_NOTES.md` using: `[SPECIFIED]`, `[PARTIALLY_SPECIFIED]`, `[UNSPECIFIED]`, or `[ASSUMPTION]`.
5. Keep paper section/equation/listing references in docstrings near corresponding node functions and graph routing functions.
6. Before changing behavior or routing logic, explain which paper requirement the change satisfies.
7. Keep graph node functions small, deterministic, and testable.
8. Add tests for state transitions, conditional routing boundaries, interrupt recovery, and edge cases.
9. Run the smallest relevant pytest after every meaningful change.
10. Do not optimize graph execution until correctness and state transition tests pass cleanly.
11. Maintain `REPRODUCTION_NOTES.md` with any deliberate deviations from the paper.
12. Maintain `VERIFICATION.md` with checked requirements and verification statuses.
