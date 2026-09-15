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