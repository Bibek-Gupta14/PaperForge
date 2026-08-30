from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from src.sql_analytics import build_sql_graph
from src.agentic_rag import build_rag_graph
from src.hitl_policy import build_hitl_graph
from src.meta_orchestrator import build_meta_graph

app = FastAPI(title="PaperForge - Graph-Based Agentic AI Dashboard")

# Global in-memory storage for active HITL sessions
hitl_sessions: Dict[str, Dict[str, Any]] = {}

class RunRequest(BaseModel):
    recipe: str  # 'sql', 'rag', 'hitl_start', 'hitl_resume', 'meta'
    query: Optional[str] = "What are total sales by region?"
    thread_id: Optional[str] = "web_thread_1"
    approval: Optional[str] = "human_approved"

@app.post("/api/run")
def run_recipe(req: RunRequest):
    if req.recipe == "sql":
        graph = build_sql_graph()
        initial_state = {
            "question": req.query,
            "schema": "", "sql": "", "error": "", "attempts": 0, "rows": [], "final_answer": "", "status": ""
        }
        res = graph.invoke(initial_state)
        return {"recipe": "SQL Analytics Repair Loop", "result": res}

    elif req.recipe == "rag":
        graph = build_rag_graph()
        initial_state = {
            "question": req.query,
            "documents": [], "graded_documents": [], "generation": "", "citation_verified": False, "retries": 0
        }
        res = graph.invoke(initial_state)
        return {"recipe": "Agentic RAG Evidence Gating", "result": res}

    elif req.recipe == "hitl_start":
        graph = build_hitl_graph()
        config = {"configurable": {"thread_id": req.thread_id}}
        initial_state = {
            "policy_id": "POL-WEB-101",
            "content": req.query,
            "risk_score": 0.0,
            "status": "",
            "approval_comment": ""
        }
        graph.invoke(initial_state, config=config)
        state_snap = graph.get_state(config)
        return {
            "recipe": "HITL Policy Review (Paused)",
            "thread_id": req.thread_id,
            "next_node": list(state_snap.next),
            "state": state_snap.values
        }

    elif req.recipe == "hitl_resume":
        graph = build_hitl_graph()
        config = {"configurable": {"thread_id": req.thread_id}}
        graph.update_state(config, {"status": req.approval})
        res = graph.invoke(None, config=config)
        return {"recipe": "HITL Policy Review (Resumed)", "result": res}

    elif req.recipe == "meta":
        graph = build_meta_graph()
        res = graph.invoke({
            "query": req.query, "intent": "", "sql_result": None, "rag_result": None, "policy_result": None, "final_output": ""
        })
        return {"recipe": "Extension Meta-Orchestrator", "result": res}

    raise HTTPException(status_code=400, detail="Unknown recipe")

@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PaperForge - Graph-Based Agentic AI Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            --card-bg: rgba(30, 41, 59, 0.7);
            --card-border: rgba(255, 255, 255, 0.1);
            --accent-purple: #8b5cf6;
            --accent-blue: #3b82f6;
            --accent-green: #10b981;
            --accent-amber: #f59e0b;
            --text-main: #f8fafc;
            --text-sub: #94a3b8;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }

        body {
            background: var(--bg-gradient);
            color: var(--text-main);
            min-height: 100vh;
            padding: 2rem;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 2.5rem;
        }

        header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(90deg, #c084fc, #60a5fa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }

        header p { color: var(--text-sub); font-size: 1.1rem; }

        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            background: rgba(139, 92, 246, 0.2);
            border: 1px solid var(--accent-purple);
            border-radius: 9999px;
            font-size: 0.85rem;
            color: #d8b4fe;
            margin-top: 0.75rem;
        }

        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
        }

        .card {
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--card-border);
            border-radius: 1rem;
            padding: 1.5rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        }

        .card h2 {
            font-size: 1.25rem;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .input-group {
            margin-bottom: 1rem;
        }

        label {
            display: block;
            font-size: 0.85rem;
            color: var(--text-sub);
            margin-bottom: 0.4rem;
        }

        input, select {
            width: 100%;
            padding: 0.75rem 1rem;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--card-border);
            border-radius: 0.5rem;
            color: white;
            font-size: 0.95rem;
            outline: none;
            transition: all 0.2s;
        }

        input:focus { border-color: var(--accent-purple); }

        .btn-group {
            display: flex;
            gap: 0.75rem;
        }

        button {
            flex: 1;
            padding: 0.75rem;
            background: linear-gradient(90deg, var(--accent-purple), var(--accent-blue));
            border: none;
            border-radius: 0.5rem;
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.2s;
        }

        button:hover { opacity: 0.9; }

        .btn-amber {
            background: linear-gradient(90deg, #f59e0b, #d97706);
        }

        .btn-green {
            background: linear-gradient(90deg, #10b981, #059669);
        }

        .output-card {
            grid-column: span 2;
        }

        pre {
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid var(--card-border);
            border-radius: 0.5rem;
            padding: 1.25rem;
            overflow-x: auto;
            color: #a7f3d0;
            font-size: 0.9rem;
            line-height: 1.5;
            max-height: 400px;
        }

        .flow-viz {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: 1rem;
            padding: 1rem;
            background: rgba(15, 23, 42, 0.4);
            border-radius: 0.5rem;
        }

        .flow-step {
            padding: 0.5rem 1rem;
            background: rgba(139, 92, 246, 0.2);
            border: 1px solid var(--accent-purple);
            border-radius: 0.4rem;
            font-size: 0.85rem;
        }

        .flow-arrow { color: var(--text-sub); font-size: 1.2rem; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>PaperForge Agentic AI Dashboard</h1>
            <p>Interactive Graph-Based Workflows (arXiv:2607.19297)</p>
            <div class="badge">LangGraph Stateful Execution Engine</div>
        </header>

        <div class="grid">
            <!-- 1. SQL Analytics Repair Loop -->
            <div class="card">
                <h2>📊 SQL Analytics Repair Loop</h2>
                <div class="input-group">
                    <label>Natural Language Analytics Prompt</label>
                    <input type="text" id="sql-query" value="What are total sales across all regions?">
                </div>
                <button onclick="runRecipe('sql')">Run SQL Graph</button>
                <div class="flow-viz">
                    <div class="flow-step">Schema</div>
                    <div class="flow-arrow">→</div>
                    <div class="flow-step">Generate</div>
                    <div class="flow-arrow">→</div>
                    <div class="flow-step">Validate</div>
                    <div class="flow-arrow">↺</div>
                    <div class="flow-step">Execute</div>
                </div>
            </div>

            <!-- 2. Agentic RAG Evidence Loop -->
            <div class="card">
                <h2>🔍 Agentic RAG Evidence Loop</h2>
                <div class="input-group">
                    <label>Search Query</label>
                    <input type="text" id="rag-query" value="What was the sales growth in Q3?">
                </div>
                <button onclick="runRecipe('rag')">Run RAG Graph</button>
                <div class="flow-viz">
                    <div class="flow-step">Retrieve</div>
                    <div class="flow-arrow">→</div>
                    <div class="flow-step">Grade</div>
                    <div class="flow-arrow">→</div>
                    <div class="flow-step">Generate</div>
                    <div class="flow-arrow">→</div>
                    <div class="flow-step">Verify</div>
                </div>
            </div>

            <!-- 3. HITL Policy Review -->
            <div class="card">
                <h2>🛡️ HITL Policy Review (Interrupt & Resume)</h2>
                <div class="input-group">
                    <label>Document Content to Review</label>
                    <input type="text" id="hitl-query" value="Confidential quarterly earnings report">
                </div>
                <div class="btn-group">
                    <button class="btn-amber" onclick="runRecipe('hitl_start')">1. Trigger & Pause</button>
                    <button class="btn-green" onclick="runRecipe('hitl_resume')">2. Approve & Resume</button>
                </div>
            </div>

            <!-- 4. Meta-Orchestrator -->
            <div class="card">
                <h2>⚡ Extension Meta-Orchestrator</h2>
                <div class="input-group">
                    <label>Multi-Intent Enterprise Query</label>
                    <input type="text" id="meta-query" value="Check total sales summary">
                </div>
                <button onclick="runRecipe('meta')">Run Meta Intent Router</button>
            </div>

            <!-- Output Container -->
            <div class="card output-card">
                <h2>📈 Live Graph Execution State</h2>
                <pre id="json-output">// Click any button above to execute state graph pathways...</pre>
            </div>
        </div>
    </div>

    <script>
        async function runRecipe(recipeType) {
            const output = document.getElementById('json-output');
            output.innerText = "Executing LangGraph state machine...";

            let query = "";
            if (recipeType === 'sql') query = document.getElementById('sql-query').value;
            if (recipeType === 'rag') query = document.getElementById('rag-query').value;
            if (recipeType === 'hitl_start' || recipeType === 'hitl_resume') query = document.getElementById('hitl-query').value;
            if (recipeType === 'meta') query = document.getElementById('meta-query').value;

            try {
                const response = await fetch('/api/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        recipe: recipeType,
                        query: query,
                        thread_id: "web_demo_thread",
                        approval: "human_approved"
                    })
                });

                const data = await response.json();
                output.innerText = JSON.stringify(data, null, 2);
            } catch (err) {
                output.innerText = "Error invoking graph: " + err;
            }
        }
    </script>
</body>
</html>
    """
