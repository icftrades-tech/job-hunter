import os
from core.models import Job, strip_html
from .base import get_json, to_eur

COUNTRY = {"es": "Spain", "gb": "United Kingdom", "nl": "Netherlands", "de": "Germany",
           "fr": "France", "it": "Italy", "us": "United States"}
CURRENCY = {"gb": "GBP", "us": "USD"}


def fetch(cfg: dict, profile: dict) -> list[Job]:
    app_id, app_key = os.getenv("ADZUNA_APP_ID"), os.getenv("ADZUNA_APP_KEY")
    if not (app_id and app_key):
        print("[adzuna] sin ADZUNA_APP_ID/KEY, omitida")
        return []
    fx = profile["salary"]["fx"]
    jobs = []
    for s in cfg["searches"]:
        c = s["country"]
        for page in range(1, cfg.get("pages", 1) + 1):
            params = {"app_id": app_id, "app_key": app_key, "results_per_page": 50,
                      "what": s["what"], "content-type": "application/json"}
            if s.get("where"):
                params["where"] = s["where"]
            data = get_json(f"https://api.adzuna.com/v1/api/jobs/{c}/search/{page}", params)
            if not data:
                break
            for r in data.get("results", []):
                cur = CURRENCY.get(c, "EUR")
                jobs.append(Job(
                    source=f"adzuna-{c}", title=r["title"],
                    company=(r.get("company") or {}).get("display_name", ""),
                    location=f'{(r.get("location") or {}).get("display_name", "")}, {COUNTRY[c]}',
                    description=strip_html(r.get("description", "")), url=r["redirect_url"],
                    salary_min=to_eur(r.get("salary_min"), cur, fx),
                    salary_max=to_eur(r.get("salary_max"), cur, fx),
                    posted=r.get("created", "")))
    return jobs
