import csv
from datetime import date, datetime
import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Configuration

JD_File = "data/job_description.md"
candidates_file = "data/candidates.jsonl"
model_path = "models/all-MiniLM-L6-v2"

top_filter = 1000
final_filter = 100

# Load candidates
candidates = []
with open(candidates_file, 'r') as f:
    for line in f:
        candidates.append(json.loads(line)) # pyright: ignore[reportUnknownMemberType]

#ketwords to look for in job description and candidate profiles

SERVICE_COMPANIES = {
    "tcs",
    "infosys",
    "wipro",
    "cognizant",
    "accenture",
    "capgemini"
}

IMPORTANT_SKILLS = {
    "python",
    "retrieval",
    "ranking",
    "search",
    "recommendation",
    "recommendation systems",
    "matching",
    "embeddings",
    "vector database",
    "vector search",
    "hybrid search",
    "information retrieval",
    "nlp",
    "bm25",
    "production",
    "deployed",
    "real users",
    "ndcg",
    "mrr",
    "map",
    "a/b testing",
    "ab testing",
    "offline evaluation",
    "online evaluation",
    "sentence-transformers",
    "openai embeddings",
    "bge",
    "e5",
    "pinecone",
    "weaviate",
    "qdrant",
    "milvus",
    "opensearch",
    "elasticsearch",
    "faiss",
    "llm",
    "fine-tuning",
    "fine-tuning llms",
    "lora",
    "qlora",
    "peft",
    "learning-to-rank",
    "learning to rank",
    "xgboost",
    "xgboost ranking",
    "reranking",
    "re-ranking",
    "transformers",
    "rag",
    "prompt engineering",
    "prompting",
    "vector search",
    "recommendation systems",
    "information retrieval",
    "offline evaluation",
    "online evaluation",
}

TARGET_TITLES = {
    "ai engineer",
    "machine learning engineer",
    "ml engineer",
    "nlp engineer",
    "search engineer",
    "relevance engineer",
    "retrieval engineer",
    "ranking engineer",
    "recommendation engineer"
}

NEGATIVE_TITLE_HINTS = {
    "qa engineer",
    "customer support",
    "operations manager",
    "marketing manager",
    "accountant",
    "civil engineer",
    "mechanical engineer",
    "sales",
    "hr manager"
}

NEGATIVE_SKILLS = {
    "computer vision",
    "object detection",
    "speech recognition",
    "tts",
    "speech",
    "robotics"
}

def safe_lower(value):
    return str(value).lower()

def load_jd(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")

def candidate_text(candidate):
    profile = candidate.get("profile", {})
    parts = [
        profile.get("headline", ""),
        profile.get("summary", ""),
        profile.get("current_title", ""),
        profile.get("current_company", ""),
        profile.get("location", ""),
        profile.get("country", ""),
    ]

    for skill in candidate.get("skills", []):
        if isinstance(skill, dict):
            parts.append(skill.get("name", ""))
        else:
            parts.append(str(skill))

    for job in candidate.get("career_history", []):
        if isinstance(job, dict):
            parts.append(job.get("title", ""))
            parts.append(job.get("company", ""))
            parts.append(job.get("description", ""))

    return " ".join(parts).lower()

def is_honeypot(candidate):
    profile = candidate.get("profile", {})
    career = candidate.get("career_history", [])
    skills = candidate.get("skills", [])

    yoe = profile.get("years_of_experience", 0)
    current_year = 2026

    if career:
        try:
            years = []
            for c in career:
                if isinstance(c, dict) and c.get("start_date"):
                    years.append(int(c["start_date"].split("-")[0]))
            if years:
                earliest_start = min(years)
                max_possible_yoe = current_year - earliest_start
                if yoe > max_possible_yoe + 2:
                    return True
        except Exception:
            pass

    expert_zero = sum(
        1 for s in skills
        if isinstance(s, dict)
        and s.get("proficiency") in ("advanced", "expert")
        and s.get("duration_months", 1) == 0
    )
    if expert_zero >= 3:
        return True

    total_career_months = sum(
        j.get("duration_months", 0)
        for j in career
        if isinstance(j, dict)
    )
    total_skill_months = sum(
        s.get("duration_months", 0)
        for s in skills
        if isinstance(s, dict)
    )

    if total_career_months > 0 and total_skill_months > total_career_months * 25:
        return True

    return False

def score_skills(candidate):
    text = candidate_text(candidate)
    skills = [
        safe_lower(s.get("name", ""))
        for s in candidate.get("skills", [])
        if isinstance(s, dict)
    ]

    score = 0.0

    for kw in IMPORTANT_SKILLS:
        if kw in skills:
            score += 4.0
        elif kw in text:
            score += 1.8

    if any(x in text for x in ["retrieval", "ranking", "recommendation"]):
        score += 8.0

    if any(x in text for x in [
        "pinecone", "qdrant", "milvus", "faiss", "weaviate",
        "elasticsearch", "opensearch"
    ]):
        score += 8.0

    if any(x in text for x in ["llm", "lora", "qlora", "peft", "fine-tuning"]):
        score += 6.0

    return score


def score_title_and_company(candidate):
    profile = candidate.get("profile", {})
    title = safe_lower(profile.get("current_title", "")) + " " + safe_lower(profile.get("headline", ""))
    company = safe_lower(profile.get("current_company", ""))

    score = 0.0

    if any(t in title for t in TARGET_TITLES):
        score += 15.0

    if any(x in title for x in ["backend", "data engineer", "search", "platform", "ml", "engineer"]):
        score += 6.0

    if any(x in title for x in NEGATIVE_TITLE_HINTS):
        score -= 18.0

    if any(svc in company for svc in SERVICE_COMPANIES):
        score -= 14.0
    else:
        score += 4.0

    return score


def score_experience(candidate):
    exp = candidate.get("profile", {}).get("years_of_experience", 0)

    if 5 <= exp <= 9:
        return 18.0
    if 4 <= exp < 5 or 9 < exp <= 12:
        return 10.0
    if exp < 3:
        return -8.0
    return 4.0


def score_negative_skills(candidate):
    text = candidate_text(candidate)
    penalty = 0.0

    for kw in NEGATIVE_SKILLS:
        if kw in text:
            penalty -= 10.0

    return penalty


def score_behavior(candidate):
    redrob = candidate.get("redrob_signals", {})
    profile = candidate.get("profile", {})

    score = 0.0

    if redrob.get("open_to_work_flag") is True:
        score += 4.0

    resp_rate = redrob.get("recruiter_response_rate", 0.0)
    if isinstance(resp_rate, (int, float)):
        score += min(max(resp_rate, 0.0), 1.0) * 5.0

    interview_rate = redrob.get("interview_completion_rate", 0.0)
    if isinstance(interview_rate, (int, float)):
        score += min(max(interview_rate, 0.0), 1.0) * 4.0

    github = redrob.get("github_activity_score", -1)
    if isinstance(github, (int, float)) and github != -1:
        score += min(max(github, 0.0), 50.0) / 10.0

    notice = redrob.get("notice_period_days", None)
    if isinstance(notice, (int, float)):
        if notice <= 15:
            score += 4.0
        elif notice <= 30:
            score += 3.0
        elif notice <= 60:
            score += 1.0
        else:
            score -= 2.0

    country = safe_lower(profile.get("country", ""))
    location = safe_lower(profile.get("location", ""))

    if country == "india" and any(x in location for x in ["pune", "noida", "delhi", "hyderabad", "mumbai"]):
        score += 3.0
    elif country == "india":
        score += 1.0
    else:
        score -= 1.0

    return score


def rule_score(candidate):
    score = 0.0
    score += score_skills(candidate)
    score += score_title_and_company(candidate)
    score += score_experience(candidate)
    score += score_negative_skills(candidate)
    score += score_behavior(candidate)
    return max(0.0, min(100.0, score))


def cosine_similarity(a, b):
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0.0:
        return 0.0
    return float(np.dot(a, b) / denom)


def build_candidate_embedding_text(candidate):
    profile = candidate.get("profile", {})
    parts = [
        profile.get("headline", ""),
        profile.get("summary", ""),
        f"Current title: {profile.get('current_title', '')}",
        f"Current company: {profile.get('current_company', '')}",
        f"Years of experience: {profile.get('years_of_experience', 0)}",
    ]

    skill_bits = []
    for s in candidate.get("skills", []):
        if not isinstance(s, dict):
            continue
        name = s.get("name", "")
        prof = s.get("proficiency", "")
        dur = s.get("duration_months", 0)
        if name:
            skill_bits.append(f"{name} ({prof}, {dur} months)")
    if skill_bits:
        parts.append("Skills: " + "; ".join(skill_bits))

    career_bits = []
    for job in candidate.get("career_history", []):
        if not isinstance(job, dict):
            continue
        career_bits.append(
            f"{job.get('title', '')} at {job.get('company', '')}. {job.get('description', '')}"
        )
    if career_bits:
        parts.append("Career: " + " | ".join(career_bits))

    return " ".join(p for p in parts if p.strip())


def generate_reasoning(candidate):
    profile = candidate.get("profile", {})
    redrob = candidate.get("redrob_signals", {})
    skills = [safe_lower(s.get("name", "")) for s in candidate.get("skills", []) if isinstance(s, dict)]

    title = profile.get("current_title", "Unknown")
    company = profile.get("current_company", "Unknown")
    exp = profile.get("years_of_experience", 0)
    country = profile.get("country", "Unknown")
    location = profile.get("location", "Unknown")

    matched = [kw for kw in IMPORTANT_SKILLS if kw in skills]
    matched = matched[:5]

    positives = []
    if matched:
        positives.append(f"matched skills: {', '.join(matched)}")
    if redrob.get("open_to_work_flag") is True:
        positives.append("open to work")
    if redrob.get("notice_period_days", 999) <= 30:
        positives.append("short notice period")
    if country == "India":
        positives.append(f"India-based ({location})")

    concerns = []
    if any(x in safe_lower(title) for x in NEGATIVE_TITLE_HINTS):
        concerns.append("title is outside the target AI/ML search profile")
    if any(svc in safe_lower(company) for svc in SERVICE_COMPANIES):
        concerns.append("current company is a service-company signal")
    if exp < 4:
        concerns.append("experience is below the preferred band")

    if redrob.get("last_active_date"):
        try:
            last_active = datetime.strptime(redrob["last_active_date"],"%Y-%m-%d").date()
            days_inactive = (date.today() - last_active).days
            if days_inactive > 180:
                concerns.append("inactive recently")
        except ValueError:
            pass

    parts = [f"{exp} years experience.", f"{title} at {company}."]
    if positives:
        parts.append("Positives: " + "; ".join(positives) + ".")
    if concerns:
        parts.append("Concerns: " + "; ".join(concerns) + ".")
    return " ".join(parts).strip()

if __name__ == "__main__":
    jd_text = load_jd(JD_File)

    # optional honeypot removal
    candidates = [c for c in candidates if not is_honeypot(c)]

    # stage 1: rule-based scoring
    rule_results = []
    for candidate in candidates:
        score = rule_score(candidate)
        rule_results.append((score, candidate))

    rule_results.sort(key=lambda x: (-x[0], x[1]["candidate_id"]))
    top_candidates = rule_results[:top_filter]

    # stage 2: semantic reranking
    model = SentenceTransformer(model_path)

    jd_embedding = model.encode(
        jd_text,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    final_results = []

    for rule_value, candidate in top_candidates:
        text = build_candidate_embedding_text(candidate)
        emb = model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        semantic_score = cosine_similarity(jd_embedding, emb)
        semantic_score = max(0.0, min(1.0, semantic_score))

        final_score = (rule_value * 0.65) + (semantic_score * 100.0 * 0.35)

        final_results.append(
            (round(final_score, 6), candidate)
        )

    final_results.sort(key=lambda x: (-x[0], x[1]["candidate_id"]))
    top_final = final_results[:final_filter]

    # write submission.csv
    with open("submission.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])

        for rank, (score, candidate) in enumerate(top_final, start=1):
            writer.writerow([
                candidate["candidate_id"],
                rank,
                f"{score:.6f}",
                generate_reasoning(candidate)
            ])

    print("submission.csv created successfully")

