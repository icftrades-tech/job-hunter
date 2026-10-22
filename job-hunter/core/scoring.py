"""Score 0-100 = suma ponderada de componentes 0-1. Pesos en config/profile.yaml."""
import re
from .filters import detect_language
from .models import Job

REGION_SCORE = {"ES": 1.0, "IE": 1.0, "REMOTE": 0.9, "EU": 0.6, "US": 0.45}


def _title(job: Job) -> float:
    t = job.title.lower()
    if re.search(r"data analyst|business analyst|analista de datos|analista de negocio", t):
        return 1.0
    if re.search(r"\bbi\b|business intelligence|analytics|reporting", t):
        return 0.8
    return 0.55


def _skills(job: Job, profile: dict) -> tuple[float, list[str], list[str]]:
    text = f"{job.title} {job.description}".lower()
    got, gaps, total = [], [], 0
    for name, sk in profile["skills"].items():
        if any(re.search(rf"(?<!\w){re.escape(a.lower())}(?!\w)", text) for a in sk["aliases"]):
            got.append(name)
            total += sk["weight"]
        else:
            gaps.append(name)
    return min(1.0, total / profile["skills_target_weight"]), got, gaps


def _seniority(job: Job) -> tuple[float, str]:
    t = job.title.lower()
    s = 0.8
    if re.search(r"junior|\bjr\b|associate|entry|graduate", t):
        s = 1.0
    elif re.search(r"senior|\bsr\b|lead|principal|staff|manager", t):
        s = 0.3
    years = [int(y) for y in re.findall(r"(\d{1,2})\+?\s*(?:years|años)", job.description.lower())]
    if years:
        need = min(years)
        s = min(s, 1.0 if need <= 3 else 0.6 if need <= 5 else 0.2)
        return s, f"pide {need}+ años"
    return s, ""


def _salary(job: Job, profile: dict) -> float:
    ceiling = job.salary_max or job.salary_min
    if not ceiling:
        return 0.5   # desconocido: neutro
    return 1.0 if ceiling >= profile["salary"]["min_annual_eur"] else 0.0


def score(job: Job, profile: dict) -> Job:
    sk, got, gaps = _skills(job, profile)
    sen, sen_note = _seniority(job)
    lang = detect_language(job.description)
    comps = {
        "title": _title(job),
        "skills": sk,
        "location": REGION_SCORE.get(job.region, 0.3),
        "seniority": sen,
        "salary": _salary(job, profile),
        "language": 1.0 if lang in ("en", "es") else 0.7,
    }
    w = profile["weights"]
    job.score = round(100 * sum(w[k] * v for k, v in comps.items()) / sum(w.values()), 1)
    reasons = []
    if got:
        reasons.append("skills: " + ", ".join(got))
    if gaps:
        reasons.append("faltan: " + ", ".join(gaps))
    if sen_note:
        reasons.append(sen_note)
    if job.region == "US":
        reasons.append("USA: revisar visado/zona horaria")
    job.reasons = reasons
    return job
