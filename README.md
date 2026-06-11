---
title: Vector Hire – RedRob Candidate Ranker
emoji: 💼
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
---

# Vector Hire — RedRob Candidate Ranker

A two-stage AI candidate ranking system built for the RedRob challenge.

## How it works

1. **Stage 1 — Rule-based scoring**: Scores each candidate using structured signals (skills, title, experience, location, behaviour).
2. **Stage 2 — Semantic reranking**: Re-ranks the top candidates using `all-MiniLM-L6-v2` cosine similarity against the job description.

## Usage

Upload a `.jsonl` or `.json` candidates file. The app returns a ranked table and a downloadable `submission.csv`.