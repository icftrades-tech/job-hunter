from core.models import Job, strip_html
from .base import get_json


def fetch(cfg: dict, profile: dict) -> list[Job]:
    jobs = []
    for token, name in cfg["companies"].items():
        data = get_json(f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs", {"content": "true"})
        if not data:
            continue
        for r in data.get("jobs", []):
            if "analy" not in r["title"].lower():
                continue
            jobs.append(Job(
                source="greenhouse", title=r["title"], company=name,
                location=(r.get("location") or {}).get("name", ""),
                description=strip_html(r.get("content", "")), url=r["absolute_url"],
                posted=r.get("updated_at", "")))
    return jobs
