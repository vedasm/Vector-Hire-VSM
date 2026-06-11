# Vector Hire — RedRob Candidate Ranker

A two-stage candidate ranking pipeline that scores and ranks the top 100 candidates from a 100K pool against a Senior AI Engineer job description. **Stage 1** uses rule-based scoring to filter down to 1,000 candidates; **Stage 2** applies semantic reranking using `all-MiniLM-L6-v2` to produce the final top 100.

## Overview
 
This repository contains the full candidate ranking pipeline for the **RedRob AI Senior AI Engineer** job description.
 
The system uses a **two-stage pipeline**:
 
1. **Stage 1 — Rule-based scoring:** Filters ~100K candidates down to the top 1,000 using signal-weighted heuristics (skills, title, experience, behavioral signals, location).
2. **Stage 2 — Semantic reranking:** Re-ranks the top 1,000 using cosine similarity between candidate embeddings and the JD embedding, computed with `all-MiniLM-L6-v2`. Final score blends both stages (65% rule / 35% semantic).

## Repository structure

```
Vector-Hire/
├── run.py                    # Core ranking logic (rule scoring + semantic reranking)
├── requirements.txt          # Python dependencies
├── submission_metadata.yaml  # Portal metadata mirror
├── data/
│   ├── job_description.md    # Target JD (Senior AI Engineer)
│   └── candidates.jsonl      # Input candidate pool (not committed — see below)
└── models/
    └── all-MiniLM-L6-v2/     # Offline model weights (see Setup)
```
## Setup

### For Windows

Prerequisites :- 
- [Git for Windows](https://git-scm.com/install/windows)
- [Git LFS](https://git-lfs.com/)

1. Set up Git LFS for your user account by running:
```
git lfs install
```
2. Clone this Repository
``` 
git clone https://github.com/vedasm/Vector-Hire.git 
```
3. Change the Directory to the project
```
cd Vector-Hire
```
4. To clone All files of model
```
git lfs pull
```

### For Linux

Install the Git LFS in Linux
```
sudo apt update
sudo apt install git-lfs
```

1. Set up Git LFS for your user account by running:
```
git lfs install
```
2. Clone this Repository
``` 
git clone https://github.com/vedasm/Vector-Hire.git 
```
3. Change the Directory to the project
```
cd Vector-Hire
```
4. To clone All files of model
```
git lfs pull
```

## For MacOS

Install with Homebrew:

1. Install git lfs
```
brew install git-lfs
```
2. Set up Git LFS:
```
git lfs install
```
3. Clone this Repository
``` 
git clone https://github.com/vedasm/Vector-Hire.git 
```
4. Change the Directory to the project
```
cd Vector-Hire
```
5. To clone All files of model
```
git lfs pull
```

## Requirements

- Python 3.10+
- CPU-only execution supported
- No external API calls
- No internet required during ranking

## Installation

1. Create a virtual environment:
```bash
python -m venv .venv
```
2. Activate it:
- Windows
```bash
.venv\Scripts\activate
```
- Linux / macOS

```bash
source .venv/bin/activate
```
3. Install Package and modules
```
pip install -r requirements.txt
```
## Model

This repository includes a local copy of:

```text
models/all-MiniLM-L6-v2
```

The ranking script loads the model from disk:

```python
model_path = "models/all-MiniLM-L6-v2"
```
Therefore no model download is required during evaluation.

## Reproducing the Submission

The following single command generates the final `submission.csv` i.e `team_Vector-Hire.csv` :

```bash
python rank.py --candidates ./data/candidates.jsonl --out ./submission.csv 
```

**📌Note :** The `candidates.jsonl` is not commited so the user must downlaod it **before running**.

This will:
- Remove honeypot / invalid candidates
- Score all candidates with rule-based heuristics
- Select the top 1,000 by rule score
- Encode all top-1,000 candidates + the JD using `all-MiniLM-L6-v2`
- Compute a blended final score (65% rule + 35% semantic)
- Write the top 100 to `submission.csv`
**Expected runtime:** ~2–4 minutes on CPU for 100K candidates.

## Validate the Submission
```
python validate_submission.py submission.csv
```
Obtained output : `Submission is valid.`

## Scoring Logic
 
### Stage 1 — Rule-based Score 
 
| Signal | Weight |
|---|---|
| Skill keyword match (skills list) | +4.0 per keyword |
| Skill keyword match (full text) | +1.8 per keyword |
| Core domain match (retrieval/ranking/recommendation) | +8.0 |
| Vector DB / search infrastructure match | +8.0 |
| LLM / fine-tuning match | +6.0 |
| Target AI/ML title match | +15.0 |
| Adjacent title match (backend, search, platform) | +6.0 |
| Non-service company | +4.0 |
| Service company (TCS, Infosys, Wipro, etc.) | −14.0 |
| Negative title (QA, sales, HR, etc.) | −18.0 |
| Negative skill domain (CV, speech, robotics) | −10.0 per match |
| Experience 5–9 yrs | +18.0 |
| Experience 4–5 or 9–12 yrs | +10.0 |
| Experience < 3 yrs | −8.0 |
| Open to work | +4.0 |
| Recruiter response rate | up to +5.0 |
| Interview completion rate | up to +4.0 |
| GitHub activity | up to +5.0 |
| Short notice period (≤15 days) | +4.0 |
| India (Pune / Noida / Delhi / Hyderabad / Mumbai) | +3.0 |
| India (other city) | +1.0 |
| Outside India | −1.0 |
 
### Stage 2 — Semantic Score
 
- JD text and candidate profile text are encoded using `all-MiniLM-L6-v2`
- Cosine similarity is computed between the JD embedding and each candidate embedding
- Normalized to [0, 1]
### Final Score
 
```
final_score = (rule_score × 0.65) + (semantic_score × 100 × 0.35)
```
 
## Honeypot Detection
 
Candidates are flagged and removed if they exhibit any of:
 
- Claimed years of experience exceed the maximum possible given their earliest career start date (with a +2 year buffer)
- Three or more skills marked `advanced`/`expert` with 0 months duration
- Total skill duration months exceed 25× their total career duration months


## Dependencies

Dependencies are specified in:
```text
requirements.txt
```
Install using:
```bash
pip install -r requirements.txt
```




