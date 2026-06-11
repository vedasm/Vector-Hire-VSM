# Vector Hire — RedRob Candidate Ranker

A two-stage candidate ranking pipeline that scores and ranks the top 100 candidates from a 100K pool against a Senior AI Engineer job description. Stage 1 uses rule-based scoring to filter down to 1,000 candidates; Stage 2 applies semantic reranking using `all-MiniLM-L6-v2` to produce the final top 100.

---

## How it works

1. **Stage 1 — Rule-based scoring**: Scores each candidate using structured signals (skills, title, experience, location, behaviour).
2. **Stage 2 — Semantic reranking**: Re-ranks the top candidates using `all-MiniLM-L6-v2` cosine similarity against the job description.

## Usage

Upload a `.jsonl` or `.json` candidates file. The app returns a ranked table and a downloadable `submission.csv`.
