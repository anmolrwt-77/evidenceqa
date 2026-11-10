import logging
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from src.config import MIN_SCORE
from src.generate import answer_question
from src.store import index_is_ready


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Shown at the top of /docs and used by the home page.
APP_DESCRIPTION = """
Grounded Q&A over official AI policy documents.

**Corpus**
- EU AI Act (Regulation 2024/1689)
- NIST AI Risk Management Framework 1.0
- NIST Generative AI Profile
- OWASP Top 10 for LLM Applications (2025/2026 markdown sources)

**How it works**
Retrieve top chunks → refuse if similarity score &lt; 0.50 → otherwise answer with citations.

**Sample questions**
1. What are the four core functions of the NIST AI Risk Management Framework?
2. Give one example of a prohibited AI practice under the EU AI Act.
3. What does the EU AI Act require regarding AI literacy of staff?
4. What is prompt injection according to OWASP?
5. Name one risk that NIST associates specifically with generative AI.
6. What is the best pizza topping in Tokyo? (should refuse)
"""

SAMPLE_QUESTIONS = [
    "What are the four core functions of the NIST AI Risk Management Framework?",
    "Give one example of a prohibited AI practice under the EU AI Act.",
    "What does the EU AI Act require regarding AI literacy of staff?",
    "What is prompt injection according to OWASP?",
    "Name one risk that NIST associates specifically with generative AI.",
    "What is the best pizza topping in Tokyo?",
]

# Update LINKEDIN_URL with your real profile before sharing with recruiters.
GITHUB_URL = "https://github.com/anmolrwt-77"
LINKEDIN_URL = "https://www.linkedin.com/in/anmolrwt77"

app = FastAPI(
    title="EvidenceQA",
    description=APP_DESCRIPTION,
    version="0.1.0",
)


class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        examples=[
            "What are the four core functions of the NIST AI Risk Management Framework?"
        ],
    )


class Citation(BaseModel):
    source: str
    index: int
    score: float


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    scores: list[float]
    refused: bool


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home() -> str:
    options = "\n".join(
        f'<option value="{q}">{q}</option>' for q in SAMPLE_QUESTIONS
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>EvidenceQA</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,500;6..72,600&display=swap" rel="stylesheet" />
  <style>
    :root {{
      --bg: #f3f6f8;
      --ink: #15202b;
      --muted: #5b6b7c;
      --accent: #0f7a66;
      --line: rgba(21, 32, 43, 0.12);
      --panel: rgba(255, 255, 255, 0.86);
      --input: #ffffff;
      --ok: #0f7a66;
      --warn: #9a6700;
      --error: #b42318;
      --shadow: 0 18px 40px rgba(21, 32, 43, 0.08);
      --glow-1: rgba(15, 122, 102, 0.14);
      --glow-2: rgba(47, 127, 158, 0.12);
      --grid: rgba(21, 32, 43, 0.04);
      --btn-text: #062018;
      --ask-shadow: 0 10px 24px rgba(15, 122, 102, 0.18);
    }}
    html[data-theme="dark"] {{
      --bg: #0b1220;
      --ink: #e8eef7;
      --muted: #9aa8bc;
      --accent: #3db8a0;
      --line: rgba(232, 238, 247, 0.12);
      --panel: rgba(17, 26, 43, 0.88);
      --input: #0c1422;
      --ok: #6ee7b7;
      --warn: #fbbf24;
      --error: #fca5a5;
      --shadow: 0 24px 60px rgba(0, 0, 0, 0.28);
      --glow-1: rgba(61, 184, 160, 0.16);
      --glow-2: rgba(47, 127, 158, 0.18);
      --grid: rgba(232, 238, 247, 0.03);
      --btn-text: #062018;
      --ask-shadow: 0 10px 24px rgba(61, 184, 160, 0.22);
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      font-family: Manrope, sans-serif;
      background:
        radial-gradient(1000px 500px at 12% -10%, var(--glow-1), transparent 55%),
        radial-gradient(800px 420px at 90% 0%, var(--glow-2), transparent 50%),
        linear-gradient(180deg, var(--bg) 0%, var(--bg) 100%);
      transition: background 0.25s ease, color 0.25s ease;
    }}
    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image:
        linear-gradient(var(--grid) 1px, transparent 1px),
        linear-gradient(90deg, var(--grid) 1px, transparent 1px);
      background-size: 48px 48px;
      mask-image: linear-gradient(180deg, rgba(0,0,0,0.45), transparent 75%);
    }}
    .wrap {{
      position: relative;
      max-width: 880px;
      margin: 0 auto;
      padding: 28px 20px 72px;
    }}
    .topbar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 56px;
      animation: fade-down 0.7s ease both;
    }}
    .brand-mark {{
      font-family: Newsreader, Georgia, serif;
      font-size: 1.15rem;
      letter-spacing: -0.02em;
    }}
    .top-actions {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }}
    .social {{
      display: flex;
      gap: 10px;
    }}
    .social a,
    #theme-toggle {{
      color: var(--muted);
      text-decoration: none;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 8px 14px;
      font-size: 0.88rem;
      font-weight: 600;
      background: transparent;
      font-family: inherit;
      cursor: pointer;
      transition: color 0.2s ease, border-color 0.2s ease, transform 0.2s ease, background 0.2s ease;
    }}
    .social a:hover,
    #theme-toggle:hover {{
      color: var(--ink);
      border-color: rgba(15, 122, 102, 0.45);
      background: rgba(15, 122, 102, 0.08);
      transform: translateY(-1px);
    }}
    .hero {{
      margin-bottom: 36px;
      animation: fade-up 0.8s ease 0.08s both;
    }}
    .hero h1 {{
      margin: 0 0 14px;
      font-family: Newsreader, Georgia, serif;
      font-size: clamp(2.6rem, 6vw, 3.6rem);
      line-height: 1.05;
      letter-spacing: -0.03em;
      font-weight: 600;
    }}
    .hero p {{
      margin: 0;
      max-width: 38rem;
      color: var(--muted);
      font-size: 1.08rem;
      line-height: 1.55;
    }}
    .corpus {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 28px 0 0;
      animation: fade-up 0.8s ease 0.18s both;
    }}
    .corpus span {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 7px 12px;
      color: var(--muted);
      font-size: 0.8rem;
      letter-spacing: 0.01em;
      background: rgba(255,255,255,0.35);
    }}
    html[data-theme="dark"] .corpus span {{
      background: rgba(255,255,255,0.02);
    }}
    .panel {{
      border: 1px solid var(--line);
      border-radius: 18px;
      background: var(--panel);
      backdrop-filter: blur(10px);
      padding: 22px;
      animation: fade-up 0.85s ease 0.24s both;
      box-shadow: var(--shadow);
    }}
    .panel h2 {{
      margin: 0 0 16px;
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--accent);
      font-weight: 700;
    }}
    label {{
      display: block;
      margin: 0 0 8px;
      font-size: 0.9rem;
      font-weight: 600;
    }}
    select, textarea {{
      width: 100%;
      margin-bottom: 14px;
      border-radius: 12px;
      border: 1px solid var(--line);
      background: var(--input);
      color: var(--ink);
      font: inherit;
      padding: 12px 14px;
      outline: none;
      transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
    }}
    select:focus, textarea:focus {{
      border-color: rgba(15, 122, 102, 0.55);
      box-shadow: 0 0 0 3px rgba(15, 122, 102, 0.12);
    }}
    textarea {{
      min-height: 100px;
      resize: vertical;
    }}
    .actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
    }}
    #ask {{
      border: none;
      border-radius: 12px;
      padding: 12px 20px;
      font: inherit;
      font-weight: 700;
      color: var(--btn-text);
      background: linear-gradient(135deg, var(--accent), #57c4d2);
      cursor: pointer;
      transition: transform 0.2s ease, filter 0.2s ease, box-shadow 0.2s ease;
      box-shadow: var(--ask-shadow);
    }}
    #ask:hover {{
      transform: translateY(-1px);
      filter: brightness(1.05);
    }}
    #ask:disabled {{
      opacity: 0.65;
      cursor: wait;
      transform: none;
    }}
    .links {{
      margin-left: auto;
      color: var(--muted);
      font-size: 0.88rem;
    }}
    .links a {{
      color: var(--ink);
      text-decoration: none;
      border-bottom: 1px solid transparent;
      transition: border-color 0.2s ease, color 0.2s ease;
    }}
    .links a:hover {{
      color: var(--accent);
      border-bottom-color: rgba(15, 122, 102, 0.6);
    }}
    #status {{
      margin-top: 16px;
      min-height: 1.3em;
      color: var(--muted);
      font-size: 0.92rem;
    }}
    #status.loading {{
      color: var(--accent);
      animation: pulse 1.2s ease-in-out infinite;
    }}
    #status.ok {{ color: var(--ok); }}
    #status.refused {{ color: var(--warn); }}
    #status.error {{ color: var(--error); }}
    #result {{
      margin-top: 10px;
      white-space: pre-wrap;
      line-height: 1.6;
      font-size: 1.02rem;
      opacity: 0;
      transform: translateY(8px);
      transition: opacity 0.35s ease, transform 0.35s ease;
    }}
    #result.show {{
      opacity: 1;
      transform: translateY(0);
    }}
    #meta {{
      margin-top: 18px;
      color: var(--muted);
      font-size: 0.92rem;
      line-height: 1.5;
      opacity: 0;
      transform: translateY(8px);
      transition: opacity 0.35s ease, transform 0.35s ease;
    }}
    #meta.show {{
      opacity: 1;
      transform: translateY(0);
    }}
    .sources-title {{
      margin: 0 0 10px;
      color: var(--ink);
      font-size: 0.82rem;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }}
    .sources-list {{
      list-style: none;
      margin: 0;
      padding: 0;
      display: grid;
      gap: 8px;
    }}
    .sources-list li {{
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 8px 16px;
      align-items: baseline;
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 12px 14px;
      background: rgba(255,255,255,0.35);
    }}
    html[data-theme="dark"] .sources-list li {{
      background: rgba(255,255,255,0.03);
    }}
    .source-main {{
      color: var(--ink);
      font-weight: 600;
      word-break: break-word;
    }}
    .source-chunk {{
      color: var(--muted);
      font-weight: 500;
      font-size: 0.88rem;
    }}
    .source-score {{
      color: var(--accent);
      font-variant-numeric: tabular-nums;
      font-weight: 700;
      font-size: 0.88rem;
      white-space: nowrap;
    }}
    footer {{
      margin-top: 28px;
      color: var(--muted);
      font-size: 0.84rem;
      animation: fade-up 0.8s ease 0.32s both;
    }}
    @keyframes fade-up {{
      from {{ opacity: 0; transform: translateY(14px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes fade-down {{
      from {{ opacity: 0; transform: translateY(-10px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes pulse {{
      0%, 100% {{ opacity: 0.55; }}
      50% {{ opacity: 1; }}
    }}
    @media (max-width: 640px) {{
      .topbar {{ margin-bottom: 36px; }}
      .actions {{ flex-direction: column; align-items: stretch; }}
      .links {{ margin-left: 0; }}
      .sources-list li {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <header class="topbar">
      <div class="brand-mark">EvidenceQA</div>
      <div class="top-actions">
        <button id="theme-toggle" type="button" aria-label="Toggle dark theme">Dark</button>
        <nav class="social" aria-label="Social links">
          <a href="{GITHUB_URL}" target="_blank" rel="noopener noreferrer">GitHub</a>
          <a href="{LINKEDIN_URL}" target="_blank" rel="noopener noreferrer">LinkedIn</a>
        </nav>
      </div>
    </header>

    <section class="hero">
      <h1>EvidenceQA</h1>
      <p>
        Grounded answers from official AI policy documents, with citations.
        Weak evidence triggers a refusal instead of a guess.
      </p>
      <div class="corpus" aria-label="Source documents">
        <span>EU AI Act</span>
        <span>NIST AI RMF 1.0</span>
        <span>NIST GenAI Profile</span>
        <span>OWASP LLM Top 10</span>
      </div>
    </section>

    <section class="panel" id="ask-panel">
      <h2>Ask the corpus</h2>
      <label for="sample">Sample questions</label>
      <select id="sample">
        <option value="">(type your own question)</option>
        {options}
      </select>

      <label for="question">Your question</label>
      <textarea id="question" placeholder="Ask about the loaded policy documents..."></textarea>

      <div class="actions">
        <button id="ask" type="button">Ask</button>
        <div class="links">
          <a href="/docs">API docs</a> ·
          <a href="/health">Health</a>
        </div>
      </div>

      <div id="status"></div>
      <div id="result"></div>
      <div id="meta"></div>
    </section>

    <footer>
      Score gate refuses below {MIN_SCORE:.2f} · Built for explainable, citation-backed policy Q&amp;A
    </footer>
  </div>

  <script>
    const sample = document.getElementById("sample");
    const question = document.getElementById("question");
    const ask = document.getElementById("ask");
    const status = document.getElementById("status");
    const result = document.getElementById("result");
    const meta = document.getElementById("meta");
    const themeToggle = document.getElementById("theme-toggle");
    const root = document.documentElement;

    function setTheme(theme) {{
      if (theme === "dark") {{
        root.setAttribute("data-theme", "dark");
        themeToggle.textContent = "Light";
        localStorage.setItem("evidenceqa-theme", "dark");
      }} else {{
        root.removeAttribute("data-theme");
        themeToggle.textContent = "Dark";
        localStorage.setItem("evidenceqa-theme", "light");
      }}
    }}

    setTheme(localStorage.getItem("evidenceqa-theme") || "light");
    themeToggle.addEventListener("click", () => {{
      const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      setTheme(next);
    }});

    function setStatus(text, kind) {{
      status.textContent = text;
      status.className = kind || "";
    }}

    function escapeHtml(text) {{
      return String(text)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
    }}

    function renderSources(citations) {{
      if (!citations || !citations.length) {{
        meta.innerHTML = '<p class="sources-title">Sources</p><p>No citations.</p>';
        meta.classList.add("show");
        return;
      }}
      const items = citations.map((c) => `
        <li>
          <div>
            <div class="source-main">${{escapeHtml(c.source)}}</div>
            <div class="source-chunk">Chunk #${{c.index}}</div>
          </div>
          <div class="source-score">score ${{c.score.toFixed(3)}}</div>
        </li>
      `).join("");
      meta.innerHTML = `
        <p class="sources-title">Sources</p>
        <ul class="sources-list">${{items}}</ul>
      `;
      meta.classList.add("show");
    }}

    sample.addEventListener("change", () => {{
      if (sample.value) {{
        question.value = sample.value;
        question.focus();
      }}
    }});

    ask.addEventListener("click", async () => {{
      const q = question.value.trim();
      result.textContent = "";
      result.classList.remove("show");
      meta.innerHTML = "";
      meta.classList.remove("show");
      if (!q) {{
        setStatus("Please enter a question.", "error");
        return;
      }}
      setStatus("Retrieving evidence... First request after idle can take about a minute.", "loading");
      ask.disabled = true;
      try {{
        const response = await fetch("/ask", {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{ question: q }}),
        }});
        const data = await response.json();
        if (!response.ok) {{
          setStatus("Error " + response.status, "error");
          result.textContent = JSON.stringify(data, null, 2);
          result.classList.add("show");
          return;
        }}
        setStatus(
          data.refused ? "Refused — evidence below score gate" : "Answered with citations",
          data.refused ? "refused" : "ok"
        );
        result.textContent = data.answer;
        result.classList.add("show");
        renderSources(data.citations);
      }} catch (err) {{
        setStatus("Request failed. Wait a moment and try again (cold start).", "error");
        result.textContent = String(err);
        result.classList.add("show");
      }} finally {{
        ask.disabled = false;
      }}
    }});
  </script>
</body>
</html>"""


@app.get("/health")
def health() -> dict:
    ready = index_is_ready()
    return {
        "status": "ok" if ready else "degraded",
        "service": "evidenceqa",
        "min_score": MIN_SCORE,
        "index_ready": ready,
    }


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    request_id = str(uuid.uuid4())[:8]
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="question must not be empty")

    if not index_is_ready():
        logger.error("request_id=%s index missing or empty", request_id)
        raise HTTPException(
            status_code=503,
            detail="Document index is not ready. Run: python scripts/build_index.py",
        )

    logger.info("request_id=%s /ask received", request_id)

    try:
        result = answer_question(question)
    except RuntimeError as exc:
        logger.error("request_id=%s failed: %s", request_id, str(exc))
        raise HTTPException(
            status_code=503,
            detail="Answer service temporarily unavailable. Please try again later.",
        ) from exc
    except Exception:
        logger.exception("request_id=%s unexpected failure", request_id)
        raise HTTPException(
            status_code=500,
            detail="Internal server error.",
        )

    logger.info(
        "request_id=%s done refused=%s citation_count=%s",
        request_id,
        result["refused"],
        len(result["citations"]),
    )

    return AskResponse(
        answer=result["answer"],
        citations=result["citations"],
        scores=result["scores"],
        refused=result["refused"],
    )