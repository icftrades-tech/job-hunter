from __future__ import annotations
import hashlib, html, re
from dataclasses import dataclass, field


def strip_html(s: str) -> str:
    s = html.unescape(s or "")
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).strip()


@dataclass
class Job:
    source: str
    title: str
    company: str
    location: str
    description: str
    url: str
    salary_min: float | None = None   # anual, EUR
    salary_max: float | None = None
    posted: str = ""
    remote: bool = False
    region: str = ""
    score: float = 0.0
    reasons: list[str] = field(default_factory=list)

    @property
    def id(self) -> str:
        key = "|".join(re.sub(r"\W+", " ", s.lower()).strip() for s in (self.company, self.title, self.location))
        return hashlib.sha1(key.encode()).hexdigest()[:16]
