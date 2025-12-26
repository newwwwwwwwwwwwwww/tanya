from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from app.rag import answer_query

app = FastAPI(title="Freshservice RAG UI")


class QueryRequest(BaseModel):
    query: str


@app.get("/", response_class=HTMLResponse)
def ui():
    return """
    <html>
    <head>
        <title>Freshservice RAG</title>
        <style>
            body { font-family: Arial; margin: 40px; }
            textarea { width: 100%; height: 100px; }
            button { padding: 10px 20px; margin-top: 10px; }
            pre { background: #f4f4f4; padding: 15px; }
        </style>
    </head>
    <body>
        <h2>Freshservice API Assistant</h2>
        <textarea id="query" placeholder="Ask a question..."></textarea><br>
        <button onclick="ask()">Ask</button>
        <h3>Answer</h3>
        <pre id="answer"></pre>

        <script>
            async function ask() {
                const q = document.getElementById("query").value;
                const res = await fetch("/query", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({query: q})
                });
                const data = await res.json();
                document.getElementById("answer").textContent =
                    data.answer + "\\n\\nSources:\\n" + data.sources.join("\\n");
            }
        </script>
    </body>
    </html>
    """


@app.post("/query")
def query_api(req: QueryRequest):
    return answer_query(req.query)
