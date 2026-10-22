import html
import json
import os
import httpx


def _fmt(r) -> str:
    sal = ""
    if r["salary_min"] or r["salary_max"]:
        sal = f' · ~{int((r["salary_max"] or r["salary_min"]) / 1000)}k€'
    reasons = "; ".join(json.loads(r["reasons"]))
    return (f'<b>{r["score"]:.0f}</b> · <a href="{html.escape(r["url"])}">{html.escape(r["title"])}</a>\n'
            f'{html.escape(r["company"])} · {html.escape(r["location"])} [{r["region"]}]{sal}\n'
            f'<i>{html.escape(reasons)}</i>')


def send(rows, dashboard_url: str = "") -> bool:
    token, chat = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    text = f"🔎 {len(rows)} vacantes nuevas\n\n" + "\n\n".join(_fmt(r) for r in rows)
    if dashboard_url:
        text += f'\n\n<a href="{dashboard_url}">Ver dashboard</a>'
    if not (token and chat):
        print("[telegram] sin credenciales; mensaje no enviado:\n" + text)
        return False
    for i in range(0, len(text), 4000):   # limite de Telegram: 4096
        r = httpx.post(f"https://api.telegram.org/bot{token}/sendMessage", timeout=30,
                       json={"chat_id": chat, "text": text[i:i + 4000], "parse_mode": "HTML",
                             "disable_web_page_preview": True})
        r.raise_for_status()
    return True
