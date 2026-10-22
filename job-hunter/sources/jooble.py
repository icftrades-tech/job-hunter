import os
from core.models import Job, strip_html
from .base import post_json


def fetch(cfg: dict, profile: dict) -> list[Job]:
    key = os.getenv("JOOBLE_API_KEY")
    if not key:
        print("[jooble] sin JOOBLE_API_KEY, omitida")
        return []
    jobs = []
    for s in cfg["searches"]:
        for page in range(1, cfg.get("pages", 1) + 1):
            data = post_json(f"https://jooble.org/api/{key}",
                             {"keywords": s["what"], "location": s["where"], "page": str(page)}) or {}
            for r in data.get("jobs", []):
                loc = r.get("location") or s["where"]
                jobs.append(Job(
                    source="jooble", title=strip_html(r.get("title", "")), company=r.get("company", ""),
                    location=f'{loc}, {s["country"]}', description=strip_html(r.get("snippet", "")),
                    url=r.get("link", ""), posted=r.get("updated", ""),
                    remote="remote" in f'{loc} {r.get("title", "")}'.lower()))
    return jobs
