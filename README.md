# PaperForge - Graph-Based Agentic AI Workflow (arXiv:2607.19297)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-StateGraph-purple.svg)](https://github.com/langchain-ai/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An independent, citation-anchored reproduction and extension of the research paper **"Graph-Based Agentic AI with LangGraph: Workflow Pathways for Long-Running Stateful Business Processes"** ([arXiv:2607.19297](https://arxiv.org/abs/2607.19297)).

---

## 🌟 Overview & Core Value

**PaperForge** converts non-deterministic, prompt-based LLM loops into explicit, auditable, and stateful **LangGraph State Graphs** (`StateGraph`). 

### Implemented Workflow Recipes
1. **SQL Analytics Repair Loop**: Formulates SQL from natural language, validates syntax, executes queries against a database (SQLite / MySQL), and automatically repairs query syntax or column errors with bounded retry limits (`attempts < 3`).
2. **Agentic RAG Evidence Loop**: Multi-stage document retrieval, relevance evidence grading, citation verification, and re-retrieval routing to eliminate ungrounded hallucinations.
3. **HITL Policy Review**: Stateful workflow featuring durable checkpoints (`MemorySaver`) and human interrupt steps (`interrupt_before=["human_review"]`).
4. **Extension Meta-Orchestrator**: Unified enterprise router classifying user intent (`'analytics'`, `'rag'`, `'policy'`) and delegating execution to the proper stateful subgraph.

---

## ⚡ Quick Start

### 1. Installation
```bash
git clone https://github.com/<YOUR_USERNAME>/PaperForge.git
cd PaperForge
pip install -r requirements.txt
```

### 2. Live OpenRouter / Nvidia Nemotron LLM Integration (Optional)
Set your OpenRouter API key to enable live generation using **Nvidia Nemotron 4 340B Instruct**:
```bash
# On Linux/macOS
export OPENROUTER_API_KEY="your-openrouter-key"

# On Windows PowerShell
$env:OPENROUTER_API_KEY="your-openrouter-key"
```
*(If no API key is set, the system automatically falls back to deterministic local mock execution).*

### 3. Run Automated Tests
```bash
python -m pytest tests/test_baseline.py -v
```

### 4. Run Minimal Paper Reproduction Benchmark
```bash
python -m scripts.reproduce_minimal
```

### 5. Launch Interactive Web Dashboard UI
```bash
python -m uvicorn src.web_server:app --port 8000
```
Open **`http://localhost:8000`** in your browser to interactively run and visually inspect live state graph executions!

---

## 📊 Reproduction Status Matrix

| Paper Recipe | Paper Claim / Goal | Paper Forge Result | Status |
| :--- | :--- | :--- | :--- |
| **SQL Repair Loop** | Validation & execution error retries | Bounded retry loop (`attempts < 3`) | `VERIFIED / MATCH` |
| **Agentic RAG** | Evidence gating & citation check | Relevance grading & citation verification pass | `VERIFIED / MATCH` |
| **HITL Policy Review**| Stateful thread interrupt & resume | `MemorySaver` checkpoint interrupt & approval resume pass | `VERIFIED / MATCH` |
| **Meta-Orchestrator** | Extension multi-subgraph intent router | Intent classification & sub-graph routing pass | `EXTENDED` |

---

## 📁 Repository Structure

```text
PaperForge/
├── src/                          # Core Graph Workflows
│   ├── sql_analytics.py          # SQL Repair Loop with OpenRouter Nemotron support
│   ├── agentic_rag.py            # Agentic RAG Evidence Gating graph
│   ├── hitl_policy.py           # HITL Policy Review with MemorySaver checkpointing
│   ├── meta_orchestrator.py      # Unified multi-recipe intent router
│   └── web_server.py             # FastAPI REST endpoints & embedded Web Dashboard
├── tests/                        # Automated Pytest Suite
│   └── test_baseline.py          # State transition & boundary tests
├── scripts/                      # Benchmark Scripts
│   └── reproduce_minimal.py      # Minimal reproduction benchmark runner
├── PAPER_SPEC.md                 # Formal implementation spec contract
├── REPRODUCTION_NOTES.md         # Paper ambiguity audit table
├── VERIFICATION.md               # Requirement verification matrix
├── TECHNICAL_ARCHITECTURE.md     # Detailed architecture blueprint
├── CLEAN_SETUP_CHECKLIST.md      # Zero-dependency setup guide
├── requirements.txt              # Production Python dependencies
└── README.md                     # Project overview & documentation
```

---

## 📄 Paper Citation

```bibtex
@article{pearson2026graphbased,
  title={Graph-Based Agentic AI with LangGraph: Workflow Pathways for Long-Running Stateful Business Processes},
  author={Pearson, Daniel and Shapiro, Sidney and Venegas, Emiliano Sebastian Gonzalez and Al-Khatib, Sanad and Arzola, Aurora Pinz{\'o}n},
  journal={arXiv preprint arXiv:2607.19297},
  year={2026}
}
```

---

## 📜 License
MIT License. Free to use, modify, and distribute for academic and enterprise research.
