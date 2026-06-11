import json, csv, io
from main import (
    is_honeypot, rule_score, build_candidate_embedding_text,
    generate_reasoning, load_jd, cosine_similarity,
    top_filter, final_filter, model_path, JD_File
)
from sentence_transformers import SentenceTransformer
import streamlit as st

@st.cache_resource
def load_model():
    return SentenceTransformer(model_path)

st.title("RedRob Candidate Ranker")

uploaded = st.file_uploader("Upload candidates (.jsonl or .json)", type=["jsonl", "json"])

if uploaded:
    content = uploaded.read().decode("utf-8")
    lines = [line.strip() for line in content.splitlines() if line.strip()]

    try:
        candidates = [json.loads(line) for line in lines]
    except json.JSONDecodeError:
        candidates = json.loads(content)
    
    candidates = [c for c in candidates if not is_honeypot(c)]

    with st.spinner("Stage 1: Rule-based scoring..."):
        rule_results = sorted(
            [(rule_score(c), c) for c in candidates],
            key=lambda x: (-x[0], x[1]["candidate_id"])
        )[:top_filter]

    model = load_model()
    jd_text = load_jd(JD_File)
    jd_emb = model.encode(jd_text, convert_to_numpy=True, normalize_embeddings=True)

    with st.spinner("Stage 2: Semantic reranking..."):
        final = []
        for rv, c in rule_results:
            emb = model.encode(build_candidate_embedding_text(c), convert_to_numpy=True, normalize_embeddings=True)
            sem = max(0.0, min(1.0, cosine_similarity(jd_emb, emb)))
            final.append((round(rv * 0.65 + sem * 100.0 * 0.35, 6), c))
        final.sort(key=lambda x: (-x[0], x[1]["candidate_id"]))
        top = final[:final_filter]

    # Display
    rows = [{"rank": i+1, "candidate_id": c["candidate_id"], "score": f"{s:.6f}", "reasoning": generate_reasoning(c)}
            for i, (s, c) in enumerate(top)]
    st.dataframe(rows)

    # Download button
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=["candidate_id","rank","score","reasoning"])
    w.writeheader(); w.writerows(rows)
    st.download_button("Download submission.csv", buf.getvalue(), "submission.csv", "text/csv")