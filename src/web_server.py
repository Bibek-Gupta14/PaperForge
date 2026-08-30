from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from src.sql_analytics import build_sql_graph
from src.agentic_rag import build_rag_graph
from src.hitl_policy import build_hitl_graph
from src.meta_orchestrator import build_meta_graph

app = FastAPI(title="PaperForge - Graph-Based Agentic Studio Platform")

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
    <title>PaperForge | Ultra-Minimal Enterprise AI Platform</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --canvas: #fefdfd;
            --surface: #ffffff;
            --obsidian: #111111;
            --charcoal: #333333;
            --subtle: #4b5563;
            --border: #e2e1d3;
            --accent: #333333;
            --cream-bg: #f9f8f3;
            --glass-white: rgba(255, 255, 255, 0.85);
            --code-bg: #111111;
            --code-text: #f3f4f6;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            -webkit-font-smoothing: antialiased;
        }

        body {
            background-color: var(--canvas);
            color: var(--obsidian);
            min-height: 100vh;
            padding: 3rem 1.5rem;
            display: flex;
            justify-content: center;
            background-size: 40px 40px;
            background-image: 
                linear-gradient(to right, rgba(51, 51, 51, 0.03) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(51, 51, 51, 0.03) 1px, transparent 1px);
        }

        .container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 4rem;
            position: relative;
        }

        .section-label {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: var(--charcoal);
            margin-bottom: 1rem;
        }

        .section-label::before {
            content: '';
            display: inline-block;
            width: 20px;
            height: 2px;
            background: var(--charcoal);
            border-radius: 2px;
        }

        header h1 {
            font-family: 'Cormorant Garamond', serif;
            font-size: 3.5rem;
            font-weight: 500;
            letter-spacing: -0.02em;
            color: var(--obsidian);
            margin-bottom: 0.75rem;
            line-height: 1.1;
        }

        header p {
            color: var(--subtle);
            font-size: 1.1rem;
            font-weight: 400;
            max-width: 680px;
            margin: 0 auto;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 2rem;
        }

        .premium-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 2.25rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 4px 16px -4px rgba(0, 0, 0, 0.06);
            transition: all 0.45s cubic-bezier(0.22, 1, 0.36, 1);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .premium-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 32px -6px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(51, 51, 51, 0.12);
            border-color: rgba(51, 51, 51, 0.25);
        }

        .premium-card h2 {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 1.2rem;
            font-weight: 600;
            letter-spacing: -0.01em;
            color: var(--obsidian);
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }

        .card-body {
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .input-group {
            margin-bottom: 1.5rem;
        }

        label {
            display: block;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--subtle);
            margin-bottom: 0.6rem;
        }

        input {
            width: 100%;
            padding: 0.9rem 1.1rem;
            background: var(--cream-bg);
            border: 1px solid var(--border);
            border-radius: 10px;
            color: var(--obsidian);
            font-size: 0.95rem;
            outline: none;
            transition: all 0.25s ease;
        }

        input:focus {
            border-color: var(--obsidian);
            background: #ffffff;
            box-shadow: 0 0 0 3px rgba(17, 17, 17, 0.08);
        }

        .btn-group {
            display: flex;
            gap: 1rem;
        }

        .btn-qbit {
            flex: 1;
            background: var(--obsidian);
            color: #ffffff;
            font-weight: 600;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 14px;
            letter-spacing: -0.01em;
            border: none;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
            box-shadow: 0 1px 3px rgba(51, 51, 51, 0.25), 0 8px 20px -8px rgba(51, 51, 51, 0.3);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        .btn-qbit:hover {
            transform: translateY(-2px) scale(1.01);
            box-shadow: 0 4px 12px rgba(51, 51, 51, 0.2), 0 14px 32px -8px rgba(51, 51, 51, 0.4);
            background: #000000;
        }

        .btn-qbit:active {
            transform: scale(0.98);
        }

        .btn-amber {
            background: #fef3c7;
            color: #92400e;
            border: 1px solid #fde68a;
            box-shadow: none;
        }

        .btn-amber:hover {
            background: #fde68a;
            color: #78350f;
            box-shadow: 0 4px 12px rgba(217, 119, 6, 0.15);
        }

        .btn-green {
            background: #d1fae5;
            color: #065f46;
            border: 1px solid #a7f3d0;
            box-shadow: none;
        }

        .btn-green:hover {
            background: #a7f3d0;
            color: #047857;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
        }

        .flow-viz {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: 1.75rem;
            padding: 0.75rem 1.1rem;
            background: var(--cream-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
        }

        .flow-step {
            padding: 0.35rem 0.75rem;
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 600;
            color: var(--subtle);
            letter-spacing: 0.02em;
            transition: all 0.2s ease;
        }

        .flow-step:hover {
            color: var(--obsidian);
            border-color: var(--obsidian);
        }

        .flow-arrow {
            color: var(--subtle);
            font-size: 0.85rem;
            opacity: 0.6;
        }

        .output-card {
            grid-column: span 2;
            margin-top: 0.5rem;
            background: var(--obsidian);
            color: #ffffff;
            border: 1px solid var(--obsidian);
        }

        .terminal-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.25rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .terminal-header h2 {
            color: #ffffff;
        }

        .terminal-dots {
            display: flex;
            gap: 0.4rem;
        }

        .dot {
            width: 9px;
            height: 9px;
            border-radius: 50%;
            background-color: rgba(255, 255, 255, 0.2);
        }

        pre {
            background: #000000;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1.5rem;
            overflow-x: auto;
            color: #10b981;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            line-height: 1.65;
            max-height: 450px;
            box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.8);
        }

        @media (max-width: 900px) {
            .grid { grid-template-columns: 1fr; }
            .output-card { grid-column: span 1; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="section-label">GRAPH ORCHESTRATION PLATFORM</div>
            <h1><b>PaperForge Agentic Platform</b></h1>
            <p>Graph-Based Workflow Pathways & Multi-Agent State Machines (arXiv:2607.19297)</p>
        </header>

        <div class="grid">
            <!-- 1. SQL Analytics Repair Loop -->
            <div class="premium-card">
                <h2>SQL Analytics Repair Loop</h2>
                <div class="card-body">
                    <div class="input-group">
                        <label>Natural Language Analytics Query</label>
                        <input type="text" id="sql-query" value="What are total sales across all regions?">
                    </div>
                    <button class="btn-qbit" onclick="runRecipe('sql')">Execute SQL Graph</button>
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
            </div>

            <!-- 2. Agentic RAG Evidence Loop -->
            <div class="premium-card">
                <h2> Agentic RAG Evidence Loop</h2>
                <div class="card-body">
                    <div class="input-group">
                        <label>Knowledge Base Search Query</label>
                        <input type="text" id="rag-query" value="What was the sales growth in Q3?">
                    </div>
                    <button class="btn-qbit" onclick="runRecipe('rag')">Execute RAG Graph</button>
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
            </div>

            <!-- 3. HITL Policy Review -->
            <div class="premium-card">
                <h2> HITL Policy Review (Interrupt & Resume)</h2>
                <div class="card-body">
                    <div class="input-group">
                        <label>Policy Document Content</label>
                        <input type="text" id="hitl-query" value="Confidential quarterly earnings report">
                    </div>
                    <div class="btn-group">
                        <button class="btn-qbit btn-amber" onclick="runRecipe('hitl_start')">1. Trigger & Pause</button>
                        <button class="btn-qbit btn-green" onclick="runRecipe('hitl_resume')">2. Approve & Resume</button>
                    </div>
                </div>
            </div>

            <!-- 4. Meta-Orchestrator -->
            <div class="premium-card">
                <h2> Extension Meta-Orchestrator</h2>
                <div class="card-body">
                    <div class="input-group">
                        <label>Multi-Intent Enterprise Prompt</label>
                        <input type="text" id="meta-query" value="Check total sales summary">
                    </div>
                    <button class="btn-qbit" onclick="runRecipe('meta')">Execute Meta Intent Router</button>
                </div>
            </div>

            <!-- Output Container -->
            <div class="premium-card output-card">
                <div class="terminal-header">
                    <h2> Live Graph Execution State</h2>
                    <div class="terminal-dots">
                        <div class="dot" style="background: green;"></div>
                        <div class="dot" style="background: yellow;"></div>
                        <div class="dot" style="background: red;"></div>
                    </div>
                </div>
                <pre id="json-output">// Click any action button above to execute state graph pathways...</pre>
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
