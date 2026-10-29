# EvidenceQA

EvidenceQA is an AI policy evidence assistant.

It answers questions using only a small set of official public documents:

the EU AI Act, the NIST AI Risk Management Framework, the NIST Generative AI profile,

and the OWASP Top 10 for LLM Applications (2026).

It retrieves relevant text, cites sources, and says "I don't know" when the documents do not contain the answer.

This is a learning project, not legal advice.

## Retrieval gate

EvidenceQA refuses to answer when the best retrieved chunk score is below **0.50**.

In that case the LLM is not called. The system returns:

`I don't know based on the provided documents.`

## Run the API locally

uvicorn src.api:app --reload --port 8000

Then open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Evaluation

Handmade eval set in `eval/questions.json`. Latest numbers are in `eval/results.md`.

## Run the UI locally

Terminal 1:

uvicorn src.api:app --reload --port 8000

Terminal 2:

streamlit run ui/[app.py](http://app.py)



## Docker (API)

Build:

docker build -t evidenceqa-api .

Run (mount local index + env):

docker run --rm -p 8000:8000 --env-file .env -v "$PWD/.chroma:/app/.chroma" evidenceqa-api

Then:

curl [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)