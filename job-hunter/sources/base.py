import time
import httpx

HEADERS = {"User-Agent": "personal-job-hunter/0.1 (uso personal)"}


def get_json(url: str, params: dict | None = None, retries: int = 2):
    for i in range(retries + 1):
        try:
            r = httpx.get(url, params=params, headers=HEADERS, timeout=30, follow_redirects=True)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            time.sleep(1)  # rate limit cortes
            return r.json()
        except httpx.HTTPError:
            if i == retries:
                raise
            time.sleep(2 * (i + 1))


def post_json(url: str, body: dict, retries: int = 2):
    for i in range(retries + 1):
        try:
            r = httpx.post(url, json=body, headers=HEADERS, timeout=30)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            time.sleep(1)
            return r.json()
        except httpx.HTTPError:
            if i == retries:
                raise
            time.sleep(2 * (i + 1))


def to_eur(value, currency: str, fx: dict) -> float | None:
    if not value or value < 5000:   # descarta horas/dias/valores raros
        return None
    return float(value) * fx.get(currency, 1.0)
