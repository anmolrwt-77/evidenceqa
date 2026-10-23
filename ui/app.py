import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"


st.set_page_config(page_title="EvidenceQA", page_icon=None, layout="centered")

st.title("EvidenceQA")
st.write(
    "Ask questions about the EU AI Act, NIST AI RMF, NIST GenAI profile, "
    "and OWASP LLM Top 10. Answers are grounded in retrieved documents."
)

question = st.text_area("Your question", height=100, placeholder="e.g. What are the four NIST AI RMF functions?")
ask = st.button("Ask", type="primary")

if ask:
    cleaned = question.strip()
    if not cleaned:
        st.warning("Please enter a question.")
    else:
        with st.spinner("Retrieving and answering..."):
            try:
                response = requests.post(
                    f"{API_URL}/ask",
                    json={"question": cleaned},
                    timeout=120,
                )
            except requests.exceptions.ConnectionError:
                st.error(
                    "Cannot connect to the API. "
                    "Start it first with: uvicorn src.api:app --reload --port 8000"
                )
                st.stop()

        if response.status_code != 200:
            st.error(f"API error {response.status_code}: {response.text}")
            st.stop()

        data = response.json()

        st.subheader("Answer")
        st.write(data["answer"])

        st.subheader("Status")
        if data["refused"]:
            st.warning("Refused by score gate (LLM was not used for a grounded answer).")
        else:
            st.success("Answered from retrieved context.")

        st.subheader("Citations")
        citations = data.get("citations") or []
        if not citations:
            st.write("(none)")
        else:
            for i, cite in enumerate(citations, start=1):
                st.markdown(
                    f"**[{i}]** `{cite['source']}` "
                    f"(index={cite['index']}, score={cite['score']:.4f})"
                )

        with st.expander("Raw scores"):
            st.write(data.get("scores", []))