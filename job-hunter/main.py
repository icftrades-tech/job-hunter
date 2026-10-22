"""Pipeline: fuentes -> dedupe -> filtros duros -> scoring -> SQLite -> Telegram -> dashboard."""
import argparse
import importlib
import os
from collections import Counter

import yaml

import dashboard
from core import filters, scoring, storage
from notify import telegram

SOURCES = ["adzuna", "infojobs", "jooble", "remotive", "remoteok", "arbeitnow", "greenhouse"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-notify", action="store_true", help="no envia Telegram ni marca como notificadas")
    ap.add_argument("--config", default="config/profile.yaml")
    args = ap.parse_args()

    try:  # .env opcional para uso local
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    profile = yaml.safe_load(open(args.config, encoding="utf-8"))

    raw = []
    for name in SOURCES:
        cfg = profile["sources"].get(name, {})
        if not cfg.get("enabled"):
            continue
        try:
            jobs = importlib.import_module(f"sources.{name}").fetch(cfg, profile)
            print(f"[{name}] {len(jobs)} vacantes")
            raw += jobs
        except Exception as e:   # una fuente rota no tumba el resto
            print(f"[{name}] ERROR: {e}")

    unique = {j.id: j for j in raw}
    drops = Counter()
    kept = []
    for j in unique.values():
        reason = filters.hard_filter(j, profile)
        if reason:
            drops[reason] += 1
        else:
            kept.append(scoring.score(j, profile))
    print(f"{len(raw)} brutas -> {len(unique)} unicas -> {len(kept)} validas. Descartes: {dict(drops)}")

    db = storage.connect()
    storage.upsert(db, kept)
    storage.prune(db, profile["dashboard"]["keep_days"])

    if not args.no_notify:
        n = profile["notify"]
        rows = storage.pending_notifications(db, n["min_score"], n["top_n"])
        if rows:
            repo = os.getenv("GITHUB_REPOSITORY", "")   # owner/repo en Actions
            url = f"https://{repo.split('/')[0]}.github.io/{repo.split('/')[1]}/" if "/" in repo else ""
            if telegram.send(rows, url):
                storage.mark_notified(db, [r["id"] for r in rows])
        else:
            print("Sin vacantes nuevas sobre el umbral")

    dashboard.build(db, profile["dashboard"]["min_score"])


if __name__ == "__main__":
    main()
