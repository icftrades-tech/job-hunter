"""Genera docs/index.html (estatico, para GitHub Pages) desde jobs.db."""
import json
from pathlib import Path

TEMPLATE = """<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Job Hunter</title>
<style>
:root{--bg:#fff;--fg:#1a1a1a;--mut:#666;--bd:#ddd;--ac:#2563eb;--card:#f7f7f8}
@media(prefers-color-scheme:dark){:root{--bg:#16181d;--fg:#e8e8e8;--mut:#9aa;--bd:#333;--ac:#6ea0ff;--card:#1f2229}}
body{margin:0;padding:16px;background:var(--bg);color:var(--fg);font:15px/1.4 system-ui,sans-serif;max-width:1000px;margin:auto}
h1{font-size:20px}.bar{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}
input,select{padding:6px 8px;border:1px solid var(--bd);border-radius:6px;background:var(--card);color:var(--fg)}
.job{border:1px solid var(--bd);background:var(--card);border-radius:8px;padding:10px 12px;margin:8px 0;display:flex;gap:12px}
.job.done{opacity:.45}.sc{font-size:22px;font-weight:700;min-width:44px;color:var(--ac)}
.m{color:var(--mut);font-size:13px}a{color:var(--ac)}button{cursor:pointer;border:1px solid var(--bd);background:none;color:var(--fg);border-radius:6px;padding:2px 8px;margin-right:4px}
</style></head><body>
<h1>Job Hunter <span class="m" id="count"></span></h1>
<div class="bar">
<input id="q" placeholder="Buscar...">
<select id="reg"><option value="">Todas las regiones</option><option>ES</option><option>IE</option><option>REMOTE</option><option>EU</option><option>US</option></select>
<select id="st"><option value="">Pendientes</option><option value="applied">Aplicadas</option><option value="dismissed">Descartadas</option><option value="all">Todas</option></select>
<label>Score ≥ <input id="min" type="number" value="45" style="width:60px"></label>
</div><div id="list"></div>
<p class="m">Actualizado: __UPDATED__</p>
<script>
const JOBS=__DATA__;
let state={};try{state=JSON.parse(localStorage.getItem('jobstate')||'{}')}catch(e){}
const save=()=>{try{localStorage.setItem('jobstate',JSON.stringify(state))}catch(e){}};
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function set(id,v){state[id]=state[id]===v?'':v;save();render()}
function render(){
 const q=document.getElementById('q').value.toLowerCase(),reg=document.getElementById('reg').value,
  st=document.getElementById('st').value,min=+document.getElementById('min').value||0;
 const rows=JOBS.filter(j=>j.score>=min&&(!reg||j.region===reg)&&(!q||(j.title+j.company+j.location).toLowerCase().includes(q))
  &&(st==='all'||(st?state[j.id]===st:!state[j.id])));
 document.getElementById('count').textContent='('+rows.length+')';
 document.getElementById('list').innerHTML=rows.map(j=>`<div class="job ${state[j.id]?'done':''}"><div class="sc">${j.score.toFixed(0)}</div><div>
 <a href="${esc(j.url)}" target="_blank" rel="noopener"><b>${esc(j.title)}</b></a><div class="m">${esc(j.company)} · ${esc(j.location)} [${j.region}] · ${esc(j.source)}${j.salary?' · ~'+Math.round(j.salary/1000)+'k€':''}</div>
 <div class="m">${esc(j.reasons.join(' · '))}</div>
 <div style="margin-top:6px"><button onclick="set('${j.id}','applied')">Aplicada</button><button onclick="set('${j.id}','dismissed')">Descartar</button></div></div></div>`).join('')}
['q','reg','st','min'].forEach(i=>document.getElementById(i).addEventListener('input',render));render();
</script></body></html>"""


def build(db, min_score: float, out: str = "docs/index.html") -> None:
    rows = db.execute("SELECT * FROM jobs WHERE score>=? ORDER BY score DESC", (min_score,)).fetchall()
    data = [{"id": r["id"], "title": r["title"], "company": r["company"], "location": r["location"],
             "region": r["region"], "url": r["url"], "source": r["source"], "score": r["score"],
             "salary": r["salary_max"] or r["salary_min"], "reasons": json.loads(r["reasons"])} for r in rows]
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    last = db.execute("SELECT MAX(last_seen) FROM jobs").fetchone()[0] or ""
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(TEMPLATE.replace("__DATA__", payload).replace("__UPDATED__", last), encoding="utf-8")
