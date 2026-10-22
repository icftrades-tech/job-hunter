from datetime import datetime, timezone
from core.models import Job, strip_html
from .base import get_json


def fetch(cfg: dict, profile: dict) -> list[Job]:
    jobs = []
    for page in range(1, cfg.get("pages", 1) + 1):
        data = get_json("https://www.arbeitnow.com/api/job-board-api", {"page": page}) or {}
        for r in data.get("data", []):
            ts = r.get("created_at")
            posted = datetime.fromtimestamp(ts, timezone.utc).isoformat() if ts else ""
            jobs.append(Job(
                source="arbeitnow", title=r["title"], company=r["company_name"],
                location=r.get("location", "") + ", Germany",
                description=strip_html(r.get("description", "")),
                url=r["url"], posted=posted, remote=bool(r.get("remote"))))
    return jobs
