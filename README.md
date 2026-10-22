# Job Hunter

Pipeline diario en GitHub Actions: busca vacantes (Adzuna, Remotive, RemoteOK, Arbeitnow, Greenhouse), filtra y puntúa según `config/profile.yaml`, avisa por Telegram y publica un dashboard en GitHub Pages.

## Puesta en marcha (≈20 min)

1. **Adzuna** (gratis): crea cuenta en https://developer.adzuna.com y copia `app_id` y `app_key`.
1b. **InfoJobs** (gratis): https://developer.infojobs.net → crea una aplicación → copia `Client ID` y `Client Secret`.
1c. **Jooble** (gratis): https://jooble.org/api/about → solicita la API key (llega por email). Agrega vacantes de Indeed y otros portales; cubre Irlanda.
2. **Telegram**: habla con `@BotFather` → `/newbot` → copia el token. Escribe cualquier mensaje a tu bot y abre `https://api.telegram.org/bot<TOKEN>/getUpdates` para ver tu `chat.id`.
3. **GitHub**: crea un repo y sube esta carpeta.
   - Settings → Secrets and variables → Actions → añade `ADZUNA_APP_ID`, `ADZUNA_APP_KEY`, `INFOJOBS_CLIENT_ID`, `INFOJOBS_CLIENT_SECRET`, `JOOBLE_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`. Las fuentes sin clave se omiten sin romper nada.
   - Settings → Pages → Source: *Deploy from a branch* → `main` / `/docs`.
   - Actions → *job-hunter* → *Run workflow* para la primera ejecución.
4. Edita `config/profile.yaml` (pesos, skills, búsquedas) y haz commit; el siguiente run lo usa.

> Pages en repos **privados** exige plan de pago. En repo público el dashboard (y `jobs.db`) serán visibles para cualquiera; `profile.yaml` también. Si te importa, usa repo privado y abre `docs/index.html` en local tras `git pull`.

## Prueba local (opcional)

```bash
pip install -r requirements.txt python-dotenv
cp .env.example .env   # rellena claves
python main.py --no-notify
```

## Notas
- Adzuna no cubre Irlanda; la cobertura irlandesa viene de remoto, Greenhouse (Stripe, Intercom...) y la ampliación de fuentes de la fase 2.
- Salario mínimo: 2.000 € netos/mes ≈ 30-31k € brutos anuales en España (12 pagas); es una aproximación y varía con tu situación fiscal. En `min_annual_eur: 30000`. En Irlanda/USA los netos se calculan distinto: los 30k brutos son solo un filtro orientativo.
- Indeed y LinkedIn: sin API pública de búsqueda y scraping contra sus términos (además bloquean las IPs de GitHub). Alternativa legítima para la fase 2: leer tus alertas de email de Indeed/LinkedIn por IMAP.
- Vacantes sin salario no se descartan (score neutro).
- Estados "Aplicada/Descartar" del dashboard se guardan solo en tu navegador.
