# Oz AI — Telegram AI boty

Telegramda öz AI botuňyz. **Mugt**, serwer **gerek däl**, kompýuter **gerek däl** —
hemme zady **telefondan** 10 minutda gurnap bolýar.

Bot islendik dilde jogap berýär we söhbeti ýatda saklaýar.

Size gerek bolan 3 zat:

1. Telegram boty tokeni (@BotFather-den)
2. OpenRouter açary (mugt AI)
3. Cloudflare hasaby (mugt — bot şol ýerde 24/7 işleýär)

---

## 1-nji ädim: Telegram bot döretmek

1. Telegramda **@BotFather** açyň → `/newbot` ýazyň.
2. Bota at beriň (mysal: `Oz AI`).
3. Username beriň, soňy `bot` bilen gutarmaly (mysal: `oz_ai_tm_bot`).
4. BotFather size **token** berer: `7123456789:AAH...` — göçürip alyň.

## 2-nji ädim: Mugt AI açary (OpenRouter)

1. https://openrouter.ai/keys açyň we giriň.
2. **Create** basyň:
   - **Expiration** → `No expiration`
   - **Credit limit** → `No limit` (hasabyňyzda pul ýok, hiç zat tölenmeýär)
3. **Create** basyň we `sk-or-v1-...` açary şol bada göçürip alyň.

Tokeni we açary telefonyňyzyň Notes (Ýazgylar) programmasyna goýup duruň.

## 3-nji ädim: Boty Cloudflare-de işletmek

1. https://dash.cloudflare.com/sign-up açyň, email bilen hasap açyň we
   emaile gelen hat bilen tassyklaň.
2. Çep menýuda **Workers & Pages** (ýa-da **Compute → Workers**) açyň.
3. **Create** → **Start with Hello World** saýlaň.
4. Ady ýazyň, mysal: `oz-ai` → **Deploy** basyň.
5. **Edit code** basyň. Içindäki ähli kody pozuň.
6. Şu faýlyň ähli kodyny göçürip goýuň:
   **[worker.js](worker.js)** (açyň → `Raw` → ählisini saýlap göçüriň)
7. Kodyň iň ýokarsyndaky iki setiri dolduryň (dyrnaklary `" "` pozmaň):
   ```js
   const TELEGRAM_TOKEN = "7123456789:AAH...";
   const AI_API_KEY = "sk-or-v1-...";
   ```
8. Sag ýokarda **Deploy** basyň.
9. Botuňyzyň salgysy görkeziler, mysal: `https://oz-ai.ADYŇYZ.workers.dev`
   Şu salgynyň soňuna **`/setup`** goşup brauzerde açyň:
   ```
   https://oz-ai.ADYŇYZ.workers.dev/setup
   ```
   **"Taýýar!"** ýazgysy çyksa — boldy! 🎉
10. Telegramda botuňyza `/start` ýazyň.

---

## Islege görä: söhbeti hemişelik ýatda saklamak

Bot söhbeti ýatda saklaýar, ýöne käwagt (Cloudflare täzelenende) ýatdakylar
arassalanyp biler. Hemişelik ýatda saklasyn diýseňiz (mugt):

1. Cloudflare-de çep menýu → **Storage & Databases → KV** → **Create** →
   ady `MEMORY` → **Add**.
2. **Workers & Pages** → `oz-ai` → **Bindings** (ýa-da **Settings → Bindings**) →
   **Add binding** → **KV namespace**.
3. **Variable name**: `MEMORY`, namespace: `MEMORY` → **Add binding / Deploy**.

## Botuň buýruklary

- `/start` — salamlaşmak
- `/new` — täze söhbet (ýatdakylary arassalaýar)
- `/id` — Telegram ID-ňizi görkezýär

## Sazlamalar

Cloudflare-de **Edit code** açyp, kodyň ýokarsynda üýtgedip bilersiňiz,
soňra **Deploy** basyň:

- `BOT_NAME` — botuň ady
- `SYSTEM_PROMPT` — botuň häsiýeti (mysal: "Sen iňlis dili mugallymy...")
- `ALLOWED_USERS` — diňe size işlesin diýseňiz: `/id` bilen ID-ňizi alyň we
  `const ALLOWED_USERS = [123456789];` diýip ýazyň

## Kynçylyklar

- **"Taýýar!" ýerine ýalňyşlyk çykýar** → `TELEGRAM_TOKEN` nädogry ýazylandyr.
  Tokeni BotFather-den gaýtadan göçürip goýuň, **Deploy** we täzeden `/setup`.
- **Bot "AI häzir jogap berip bilmedi" diýýär** → `AI_API_KEY` nädogry ýa-da
  mugt limit wagtlaýyn gutardy. Birnäçe minutdan synanyşyň.
- **Bot asla jogap bermeýär** → `/setup` salgysyny açdyňyzmy? Kody üýtgedip
  **Deploy** edeniňizden soň hem `/setup`-y täzeden açyň.
- Ýalňyşlyklary görmek: Cloudflare → `oz-ai` → **Logs** / **Observability**.

---

## Öz serweriňizde (bir buýruk bilen)

Ubuntu/Debian serwere SSH bilen giriň we şu buýrugy goýuň:

```bash
curl -fsSL https://raw.githubusercontent.com/k9032431-cmd/TelegramAI/ccr-1ece83d6-3yt3px/install.sh | sudo bash
```

Skript hemme zady özi edýär: Docker gurnaýar, kody alýar, sizden Telegram
tokenini we OpenRouter açaryny soraýar (ikisini hem barlaýar) we boty işledýär.
Bot serwer täzeden açylanda-da özi başlaýar.

Täzelemek üçin şol buýrugy gaýtadan işlediň.

Peýdaly buýruklar:

```bash
cd /opt/oz-ai/server
docker compose logs -f      # loglary görmek (Ctrl+C - çykmak)
docker compose restart      # täzeden başlatmak
nano .env                   # sazlamalary üýtgetmek (soňra restart)
```

Python wersiýasy `server/` bukjasynda. Ol Groq, Gemini, OpenRouter we
OpenAI-a meňzeş islendik API bilen işleýär.
