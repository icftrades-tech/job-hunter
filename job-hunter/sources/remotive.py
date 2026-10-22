from core.models import Job, strip_html
from .base import get_json


def fetch(cfg: dict, profile: dict) -> list[Job]:
    jobs = []
    for q in cfg["searches"]:
        data = get_json("https://remotive.com/api/remote-jobs", {"search": q}) or {}
        for r in data.get("jobs", []):
            jobs.append(Job(
                source="remotive", title=r["title"], company=r["company_name"],
                location=f'Remote - {r.get("candidate_required_location", "")}',
                description=strip_html(r.get("description", "")), url=r["url"],
                posted=r.get("publication_date", ""), remote=True))
    return jobs
