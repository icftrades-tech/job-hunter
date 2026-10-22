"""Filtros duros: devuelven un motivo de descarte o None si la vacante pasa."""
import re
from .models import Job

ES = ["spain", "españa", "madrid", "barcelona", "valencia", "sevilla", "seville", "bilbao", "málaga", "malaga", "zaragoza"]
IE = ["ireland", "irlanda", "dublin", "cork", "galway", "limerick"]
EU = ["germany", "berlin", "munich", "hamburg", "netherlands", "amsterdam", "rotterdam", "france", "paris",
      "italy", "milan", "portugal", "lisbon", "porto", "belgium", "brussels", "austria", "vienna", "poland",
      "warsaw", "sweden", "stockholm", "denmark", "copenhagen", "finland", "helsinki", "norway", "switzerland",
      "zurich", "united kingdom", "london", "uk", "czech", "prague", "luxembourg", "greece", "romania"]
US = ["united states", "usa", "u.s.", "us only", "new york", "san francisco", "california", "texas", "seattle",
      "boston", "chicago", "austin", "remote - us", "north america", "americas"]
EUROPE_REMOTE = ["europe", "emea", "worldwide", "anywhere", "global", "eu"]
NOT_WANTED = ["canada", "latam", "latin america", "india", "australia", "brazil", "mexico", "asia", "apac",
              "singapore", "japan", "philippines", "africa"]

EN_WORDS = set("the and to of in for with you we will is are our your experience team work".split())
ES_WORDS = set("el la los las para con un una del por se nuestro experiencia equipo trabajo requisitos".split())
OTHER_WORDS = set("der die das und mit für wir sie nicht ein eine auf het een van voor et les des pour nous vous "
                  "il che per con gli le".split())


def _has(text: str, words: list[str]) -> bool:
    return any(re.search(rf"(?<!\w){re.escape(w)}(?!\w)", text) for w in words)


def classify_region(job: Job) -> str:
    loc = job.location.lower()
    if _has(loc, ES):
        return "ES"
    if _has(loc, IE):
        return "IE"
    if _has(loc, US):
        return "US"
    if _has(loc, EU):
        return "EU"
    if _has(loc, EUROPE_REMOTE):
        return "REMOTE"
    if _has(loc, NOT_WANTED):
        return "OTHER"
    if job.remote:   # remoto sin restriccion geografica explicita
        return "REMOTE"
    return "OTHER"


def detect_language(text: str) -> str:
    words = re.findall(r"[a-záéíóúñüäöß]+", text[:1500].lower())
    if len(words) < 30:
        return "unknown"
    en, es, other = (sum(w in s for w in words) for s in (EN_WORDS, ES_WORDS, OTHER_WORDS))
    if other > max(en, es):
        return "other"
    return "en" if en >= es else "es"


def hard_filter(job: Job, profile: dict) -> str | None:
    t = job.title.lower()
    s = profile["search"]
    if not _has(t, [w.lower() for w in s["titles_include"]]):
        return "titulo no relevante"
    if _has(t, [w.lower() for w in s["titles_exclude"]]):
        return "titulo excluido"
    job.region = classify_region(job)
    if job.region == "OTHER":
        return "region no deseada"
    if job.region == "US" and not profile["location"]["accept_us"]:
        return "USA desactivado"
    if detect_language(job.description) == "other":
        return "idioma ni ingles ni espanol"
    ceiling = job.salary_max or job.salary_min
    if ceiling and ceiling < profile["salary"]["min_annual_eur"]:
        return "salario bajo el minimo"
    return None
