"""
Web Demo — Giao diện web cho Chatbot vs Agent.
Chạy: python web_demo.py → Mở trình duyệt: http://localhost:5000
"""
import os
import sys
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template_string, request, jsonify
from dotenv import load_dotenv
from src.chatbot import run_chatbot
from src.agent.agent import ReActAgent
from src.core.openai_provider import OpenAIProvider
from src.tools.shopping_tools import TOOLS

load_dotenv()

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lab 3 — Chatbot vs ReAct Agent</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #e2e8f0;
            min-height: 100vh;
        }
        .header {
            text-align: center;
            padding: 30px 20px 20px;
            background: rgba(15, 23, 42, 0.8);
            border-bottom: 1px solid rgba(99, 102, 241, 0.3);
        }
        .header h1 {
            font-size: 1.8rem;
            background: linear-gradient(90deg, #818cf8, #a78bfa, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .header p { color: #94a3b8; margin-top: 5px; font-size: 0.9rem; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .input-area {
            display: flex; gap: 10px; margin-bottom: 20px;
        }
        .input-area input {
            flex: 1; padding: 14px 18px; border-radius: 12px;
            border: 1px solid rgba(99, 102, 241, 0.3);
            background: rgba(30, 41, 59, 0.8); color: #e2e8f0;
            font-size: 1rem; outline: none; transition: border 0.3s;
        }
        .input-area input:focus { border-color: #818cf8; }
        .input-area button {
            padding: 14px 28px; border-radius: 12px; border: none;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: white; font-weight: 600; cursor: pointer;
            font-size: 1rem; transition: transform 0.2s, opacity 0.2s;
        }
        .input-area button:hover { transform: translateY(-2px); opacity: 0.9; }
        .input-area button:disabled { opacity: 0.5; cursor: wait; }
        .results { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .card {
            background: rgba(30, 41, 59, 0.6); border-radius: 16px;
            border: 1px solid rgba(99, 102, 241, 0.15);
            overflow: hidden; backdrop-filter: blur(10px);
        }
        .card-header {
            padding: 15px 20px; font-weight: 600; font-size: 1.1rem;
            display: flex; align-items: center; gap: 10px;
        }
        .card-chatbot .card-header { background: linear-gradient(90deg, rgba(59,130,246,0.15), transparent); color: #60a5fa; }
        .card-agent .card-header { background: linear-gradient(90deg, rgba(168,85,247,0.15), transparent); color: #c084fc; }
        .card-body { padding: 20px; min-height: 200px; }
        .card-body p { line-height: 1.7; white-space: pre-wrap; }
        .stats {
            padding: 12px 20px; border-top: 1px solid rgba(99,102,241,0.1);
            display: flex; gap: 20px; font-size: 0.8rem; color: #94a3b8;
        }
        .stats span { display: flex; align-items: center; gap: 4px; }
        .loading { text-align: center; padding: 40px; color: #94a3b8; }
        .loading .spinner {
            width: 30px; height: 30px; border: 3px solid rgba(99,102,241,0.2);
            border-top-color: #818cf8; border-radius: 50%;
            animation: spin 0.8s linear infinite; margin: 0 auto 10px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .suggestions {
            display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px;
        }
        .suggestions button {
            padding: 8px 16px; border-radius: 20px;
            border: 1px solid rgba(99,102,241,0.3);
            background: rgba(30,41,59,0.5); color: #cbd5e1;
            font-size: 0.85rem; cursor: pointer; transition: all 0.2s;
        }
        .suggestions button:hover {
            background: rgba(99,102,241,0.2); border-color: #818cf8; color: white;
        }
        .trace { margin-top: 10px; padding: 12px; background: rgba(0,0,0,0.3);
            border-radius: 8px; font-size: 0.8rem; color: #94a3b8;
            max-height: 200px; overflow-y: auto;
        }
        .trace-step { margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid rgba(99,102,241,0.1); }
        .trace-thought { color: #fbbf24; }
        .trace-action { color: #34d399; }
        .trace-obs { color: #60a5fa; }
        @media (max-width: 768px) { .results { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="header">
        <h1>Lab 3 — Chatbot vs ReAct Agent</h1>
        <p>Nhom 30 — Trinh Ke Tien | Tro Ly Mua Sam Thong Minh</p>
    </div>
    <div class="container">
        <div class="suggestions">
            <button onclick="ask('Tim laptop duoi 15 trieu')">Laptop duoi 15 trieu</button>
            <button onclick="ask('So sanh Acer Aspire 5 voi ASUS Vivobook 15')">So sanh 2 laptop</button>
            <button onclick="ask('Tim phone')">Dien thoai</button>
            <button onclick="ask('Danh gia iPhone 15')">Review iPhone 15</button>
            <button onclick="ask('Tim headphone')">Tai nghe</button>
            <button onclick="ask('Tim smartwatch')">Dong ho thong minh</button>
            <button onclick="ask('Tim camera')">May anh</button>
            <button onclick="ask('So sanh Sony WH-1000XM5 voi Apple AirPods Pro 2')">So sanh tai nghe</button>
            <button onclick="ask('Tim may giat')">May giat (edge case)</button>
        </div>
        <div class="input-area">
            <input type="text" id="query" placeholder="Nhap cau hoi..." onkeydown="if(event.key==='Enter')sendQuery()">
            <button id="sendBtn" onclick="sendQuery()">Gui</button>
        </div>
        <div class="results">
            <div class="card card-chatbot">
                <div class="card-header">🤖 Chatbot (Baseline)</div>
                <div class="card-body" id="chatbot-result"><p style="color:#64748b">Chua co cau tra loi</p></div>
                <div class="stats" id="chatbot-stats"></div>
            </div>
            <div class="card card-agent">
                <div class="card-header">🧠 ReAct Agent</div>
                <div class="card-body" id="agent-result"><p style="color:#64748b">Chua co cau tra loi</p></div>
                <div class="stats" id="agent-stats"></div>
            </div>
        </div>
    </div>
    <script>
        function ask(q) { document.getElementById('query').value = q; sendQuery(); }
        async function sendQuery() {
            const q = document.getElementById('query').value.trim();
            if (!q) return;
            const btn = document.getElementById('sendBtn');
            btn.disabled = true; btn.textContent = 'Dang xu ly...';
            document.getElementById('chatbot-result').innerHTML = '<div class="loading"><div class="spinner"></div>Dang hoi Chatbot...</div>';
            document.getElementById('agent-result').innerHTML = '<div class="loading"><div class="spinner"></div>Dang hoi Agent...</div>';
            document.getElementById('chatbot-stats').innerHTML = '';
            document.getElementById('agent-stats').innerHTML = '';
            try {
                const res = await fetch('/ask', {
                    method: 'POST', headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({query: q})
                });
                const data = await res.json();
                document.getElementById('chatbot-result').innerHTML = '<p>' + data.chatbot.answer + '</p>';
                document.getElementById('chatbot-stats').innerHTML =
                    '<span>⏱️ ' + data.chatbot.latency_ms + 'ms</span>' +
                    '<span>🪙 ' + data.chatbot.tokens + ' tokens</span>' +
                    '<span>📊 1 step</span>';
                let agentHtml = '<p>' + data.agent.answer + '</p>';
                if (data.agent.trace && data.agent.trace.length > 0) {
                    agentHtml += '<div class="trace"><b>Trace:</b>';
                    data.agent.trace.forEach(function(s) {
                        agentHtml += '<div class="trace-step">';
                        agentHtml += '<div><b>Step ' + s.step + '</b></div>';
                        if (s.thought) agentHtml += '<div class="trace-thought">Thought: ' + s.thought + '</div>';
                        if (s.action) agentHtml += '<div class="trace-action">Action: ' + s.action + '</div>';
                        if (s.observation) agentHtml += '<div class="trace-obs">Obs: ' + s.observation.substring(0,150) + '...</div>';
                        agentHtml += '</div>';
                    });
                    agentHtml += '</div>';
                }
                document.getElementById('agent-result').innerHTML = agentHtml;
                document.getElementById('agent-stats').innerHTML =
                    '<span>⏱️ ' + data.agent.latency_ms + 'ms</span>' +
                    '<span>🪙 ' + data.agent.tokens + ' tokens</span>' +
                    '<span>📊 ' + data.agent.steps + ' steps</span>';
            } catch(e) {
                document.getElementById('chatbot-result').innerHTML = '<p style="color:#f87171">Loi: ' + e + '</p>';
                document.getElementById('agent-result').innerHTML = '<p style="color:#f87171">Loi: ' + e + '</p>';
            }
            btn.disabled = false; btn.textContent = 'Gui';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/ask', methods=['POST'])
def ask():
    query = request.json.get('query', '')

    # Chatbot
    chatbot_result = run_chatbot(query)

    # Agent
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("DEFAULT_MODEL", "gpt-4o")
    llm = OpenAIProvider(model_name=model, api_key=api_key)
    agent = ReActAgent(llm=llm, tools=TOOLS, max_steps=5)
    agent_answer = agent.run(query)

    total_tokens = sum(s["tokens"].get("total_tokens", 0) for s in agent.trace)
    total_ms = sum(s["latency_ms"] for s in agent.trace)

    # Parse trace cho frontend
    trace_data = []
    for s in agent.trace:
        step_info = {"step": s["step"]}
        text = s["llm_output"]
        if "Thought:" in text:
            thought = text.split("Thought:")[-1].split("Action:")[0].split("Final Answer:")[0].strip()
            step_info["thought"] = thought
        if "action" in s:
            step_info["action"] = s["action"]
        if "observation" in s:
            step_info["observation"] = s["observation"]
        trace_data.append(step_info)

    return jsonify({
        "chatbot": {
            "answer": chatbot_result["content"],
            "tokens": chatbot_result["usage"]["total_tokens"],
            "latency_ms": chatbot_result["latency_ms"],
        },
        "agent": {
            "answer": agent_answer,
            "tokens": total_tokens,
            "latency_ms": total_ms,
            "steps": len(agent.trace),
            "trace": trace_data,
        }
    })

if __name__ == '__main__':
    print("=" * 50)
    print("  Mo trinh duyet: http://localhost:5000")
    print("=" * 50)
    app.run(debug=False, port=5000)
