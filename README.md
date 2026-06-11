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
