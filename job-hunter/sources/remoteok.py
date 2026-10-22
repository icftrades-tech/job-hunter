from core.models import Job, strip_html
from .base import get_json, to_eur


def fetch(cfg: dict, profile: dict) -> list[Job]:
    fx = profile["salary"]["fx"]
    data = get_json("https://remoteok.com/api") or []
    jobs = []
    for r in data:
        if not isinstance(r, dict) or "position" not in r:
            continue  # el primer elemento es un aviso legal
        jobs.append(Job(
            source="remoteok", title=r["position"], company=r.get("company", ""),
            location=f'Remote - {r.get("location", "")}', description=strip_html(r.get("description", "")),
            url=r.get("url", ""), salary_min=to_eur(r.get("salary_min"), "USD", fx),
            salary_max=to_eur(r.get("salary_max"), "USD", fx), posted=r.get("date", ""), remote=True))
    return jobs
