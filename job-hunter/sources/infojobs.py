import base64
import os
import re
from core.models import Job, strip_html
from .base import HEADERS, get_json
import httpx

API = "https://api.infojobs.net/api/9"


def _get(path: str, params: dict, auth: str):
    r = httpx.get(f"{API}{path}", params=params, headers={**HEADERS, "Authorization": f"Basic {auth}"}, timeout=30)
    if r.status_code in (401, 403):
        raise RuntimeError(f"InfoJobs {r.status_code}: revisa INFOJOBS_CLIENT_ID/SECRET")
    r.raise_for_status()
    return r.json()


def _annual(item: dict) -> tuple[float | None, float | None]:
    period = ((item.get("salaryPeriod") or {}).get("value") or "").lower()
    mult = 12 if "mes" in period else 1 if "año" in period or "ano" in period else 0
    lo = (item.get("salaryMin") or {}).get("amount")
    hi = (item.get("salaryMax") or {}).get("amount")
    if not mult:
        return None, None
    return (lo * mult if lo else None), (hi * mult if hi else None)


def fetch(cfg: dict, profile: dict) -> list[Job]:
    cid, secret = os.getenv("INFOJOBS_CLIENT_ID"), os.getenv("INFOJOBS_CLIENT_SECRET")
    if not (cid and secret):
        print("[infojobs] sin INFOJOBS_CLIENT_ID/SECRET, omitida")
        return []
    auth = base64.b64encode(f"{cid}:{secret}".encode()).decode()
    jobs, details = [], 0
    for q in cfg["searches"]:
        for page in range(1, cfg.get("pages", 1) + 1):
            data = _get("/offer", {"q": q, "maxResults": 50, "page": page}, auth)
            for it in data.get("items", []):
                lo, hi = _annual(it)
                desc = ""
                # el listado no trae descripcion: la pedimos solo para titulos relevantes (limite de llamadas)
                if details < cfg.get("max_details", 40) and re.search(r"analy|datos|\bbi\b|intelligence", it["title"].lower()):
                    try:
                        desc = strip_html(_get(f'/offer/{it["id"]}', {}, auth).get("description", ""))
                        details += 1
                    except Exception:
                        pass
                jobs.append(Job(
                    source="infojobs", title=it["title"], company=(it.get("author") or {}).get("name", ""),
                    location=f'{it.get("city", "")}, {(it.get("province") or {}).get("value", "")}, Spain',
                    description=desc or strip_html(it.get("requirementMin", "")), url=it["link"],
                    salary_min=lo, salary_max=hi, posted=it.get("published", ""),
                    remote="remot" in it["title"].lower()))
    return jobs
