# Oz AI — Telegram AI boty

Telegramda öz AI botuňyz. **Mugt** AI API-lar bilen işleýär (Groq, Google Gemini, OpenRouter),
söhbeti ýatda saklaýar, islendik dilde jogap berýär we serwerde aňsat işledilýär.

## Näme edip bilýär

- Islendik soraga AI bilen jogap berýär
- Soňky habarlary ýatda saklaýar (söhbeti dowam etdirýär)
- `/new` — täze söhbet, `/id` — Telegram ID-ňizi görkezýär
- Islege görä diňe size (ýa-da saýlan adamlaryňyza) işleýär

---

## 1-nji ädim: Telegram bot döretmek (2 minut)

1. Telegramda **@BotFather** tapyň we `/start` basyň.
2. `/newbot` ýazyň.
3. Bota at beriň (mysal: `Oz AI`).
4. Username beriň, `bot` bilen gutarmaly (mysal: `oz_ai_tm_bot`).
5. BotFather size **token** berer, şeýle görnüşde: `7123456789:AAH...`
   Muny göçürip alyň — hiç kime görkezmäň!

## 2-nji ädim: Mugt AI açaryny almak

**Groq** maslahat berilýär (mugt, örän çalt):

1. https://console.groq.com açyň we Google bilen giriň.
2. Çepde **API Keys** → **Create API Key**.
3. Açary göçürip alyň (`gsk_...` bilen başlaýar).

Başga mugt wariantlar:

| Üpjün ediji | Açar almak | `AI_PROVIDER` |
|---|---|---|
| Groq | https://console.groq.com/keys | `groq` |
| Google Gemini | https://aistudio.google.com/apikey | `gemini` |
| OpenRouter | https://openrouter.ai/keys | `openrouter` |

> Bellik: käbir ýurtlarda bu saýtlar açylmasa, VPN gerek bolup biler.
> Serweriňiz daşary ýurtda bolsa, bot özi kadaly işleýär.

## 3-nji ädim: Sazlamak

`.env.example` faýlyny `.env` diýip göçüriň we içini dolduryň:

```
TELEGRAM_TOKEN=BotFather-den alan tokeniňiz
AI_PROVIDER=groq
AI_API_KEY=gsk_...
```

---

## 4-nji ädim: Işletmek

### A) Öz kompýuteriňizde synap görmek

[Python 3.10+](https://www.python.org/downloads/) gurnalan bolmaly.

```bash
pip install -r requirements.txt
python bot.py
```

Indi Telegramda botuňyza `/start` ýazyň. Kompýuter öçse, bot hem durýar —
hemişe işlemegi üçin serwer gerek.

### B) Serwerde işletmek (Docker bilen — iň aňsat)

Islendik arzan Linux VPS (Ubuntu 22.04/24.04) ýeterlik: 1 CPU, 512 MB–1 GB RAM.
Mugt wariantlar hem bar: Oracle Cloud Free Tier, Google Cloud e2-micro.

Serwere SSH bilen giriň we şulary ýazyň:

```bash
# 1. Docker gurnamak
curl -fsSL https://get.docker.com | sh

# 2. Kody almak
git clone https://github.com/k9032431-cmd/TelegramAI.git
cd TelegramAI

# 3. Sazlamak
cp .env.example .env
nano .env        # tokeni we açary ýazyň, Ctrl+O, Enter, Ctrl+X bilen ýapyň

# 4. Işletmek
docker compose up -d --build
```

Boldy! Bot fon režiminde işleýär we serwer täzeden açylanda-da özi başlaýar.

Peýdaly buýruklar:

```bash
docker compose logs -f        # botuň loglaryny görmek (Ctrl+C bilen çykyň)
docker compose restart        # .env üýtgedeniňizden soň
docker compose down           # botu duruzmak
git pull && docker compose up -d --build   # kody täzelemek
```

---

## Sazlamalar (`.env`)

| Üýtgeýji | Näme üçin | Mysal |
|---|---|---|
| `TELEGRAM_TOKEN` | BotFather tokeni (hökmany) | `7123:AAH...` |
| `AI_API_KEY` | AI açary (hökmany) | `gsk_...` |
| `AI_PROVIDER` | `groq`, `gemini`, `openrouter` | `groq` |
| `AI_MODEL` | Modeli üýtgetmek | `llama-3.1-8b-instant` |
| `AI_BASE_URL` | Başga OpenAI-a meňzeş API | `http://localhost:11434/v1` |
| `BOT_NAME` | Botuň ady | `Oz AI` |
| `SYSTEM_PROMPT` | Botuň häsiýeti, özüni nähili alyp barmaly | `Sen mugallym...` |
| `ALLOWED_USERS` | Diňe şu ID-ler ulanyp bilsin | `123456789,987654321` |
| `HISTORY_LIMIT` | Ýatda saklanýan habar sany | `20` |

**Botuňyzy diňe özüňize açmak:** bota `/id` ýazyň, ID-ni `.env`-däki
`ALLOWED_USERS=` ýanyna ýazyň we `docker compose restart` ediň.

**Soňra tölegli AI-a geçmek:** OpenAI-a meňzeş islendik API işleýär —
diňe `AI_BASE_URL`, `AI_API_KEY` we `AI_MODEL` üýtgediň, kod üýtgemeýär.

## Kynçylyklar

- **Bot jogap bermeýär** → `docker compose logs -f` bilen ýalňyşlygy görüň.
  Köplenç token ýa-da API açar nädogry bolýar.
- **"AI häzir jogap berip bilmedi"** → mugt limit gutaran bolmagy ähtimal
  (birnäçe minutdan gaýtadan synanyşyň) ýa-da model ady köne. Üpjün edijiň
  saýtynda häzirki model atlaryna seredip, `AI_MODEL` bilen beriň.
- **Ýatda saklamak** → bot täzeden başlanda söhbetler arassalanýar, bu kadaly.
