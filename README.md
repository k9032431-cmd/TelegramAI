# 🤖 Telegram AI Bot (mugt)

Telegramda öz AI kömekçiňiz. Mugt AI hyzmatlaryny ulanýar (Groq, Google Gemini ýa-da OpenRouter), şonuň üçin size **hiç hili çykdajy ýok**.

**Näme edip bilýär:**
- Islendik soraga jogap berýär (türkmençe, rusça, iňlisçe...)
- Gürrüňi ýatda saklaýar (soňky 20 habary)
- `/reset` – ýady arassalaýar
- Diňe saýlanan adamlara rugsat berip bolýar

---

## 📚 Ilki bilen: bu nähili işleýär?

```
Siz (Telegram)  →  Telegram serweri  →  bot.py (siziň kompýuteriňiz/serweriňiz)
                                            ↓
                                     Mugt AI (Groq)
                                            ↓
Siz (Telegram)  ←  Telegram serweri  ←  bot.py jogaby iberýär
```

`bot.py` – bu ýönekeý programma. Ol hemişe "diňleýär": Telegramda kimdir biri bota ýazsa, ol habary alýar, AI-a iberýär we AI-yň jogabyny yzyna ugradýar.

### Faýllar näme?

| Faýl | Näme üçin |
|---|---|
| `bot.py` | Botuň esasy kody (içinde her bölüm düşündirilen) |
| `requirements.txt` | Python-a gerek goşmaça kitaphanalaryň sanawy |
| `.env.example` | Sazlamalaryň nusgasy. Siz ony `.env` edip göçürýärsiňiz |
| `.env` | Siziň gizlin açarlaryňyz (**hiç kime görkezmäň!**) |
| `Dockerfile`, `docker-compose.yml` | Serwerde aňsat işletmek üçin |

---

## 🔑 1-nji ädim: Iki sany "açar" alyň (ikisi hem mugt)

### A) Telegram bot tokeni
1. Telegramda **@BotFather** tapyň we `/newbot` ýazyň.
2. Bota at beriň (meselem: `Meniň AI`).
3. Ulanyjy adyny beriň, `bot` bilen gutarmaly (meselem: `menin_ai_bot`).
4. BotFather size şeýle token berer: `7123456789:AAH...`. Şony saklaň.

### B) Mugt AI açary (Groq – maslahat berilýär)
1. **https://console.groq.com** saýtyna giriň (Google hasaby bilen bolýar).
2. Çepde **API Keys** → **Create API Key**.
3. `gsk_...` bilen başlaýan açary göçürip alyň.

> 💡 Groq işlemese, **Google Gemini** (https://aistudio.google.com/apikey) ýa-da **OpenRouter** (https://openrouter.ai/keys) ulanyp bilersiňiz. `.env.example` faýlynda üçüsiniň hem nusgasy bar.

---

## 💻 2-nji ädim: Öz kompýuteriňizde işletmek

### Python guruň
- https://www.python.org/downloads/ saýtyndan Python 3.10 ýa-da ondan täzesini ýükläň.
- **Windows**-da gurnanyňyzda **"Add Python to PATH"** diýen ýere bellik goýmagy ýatdan çykarmaň!

### Kody ýükläň we işlediň
Terminaly açyň (Windows: `cmd`, Mac/Linux: `Terminal`) we tertip bilen ýazyň:

```bash
# 1. Kody göçürip alyň
git clone https://github.com/k9032431-cmd/TelegramAI.git
cd TelegramAI

# 2. Aýratyn "gutujyk" (virtual gurşaw) dörediň
python -m venv venv

# 3. Ony işjeňleşdiriň
#    Windows:
venv\Scripts\activate
#    Mac/Linux:
source venv/bin/activate

# 4. Gerekli kitaphanalary guruň
pip install -r requirements.txt

# 5. Sazlamalar faýlyny dörediň
#    Windows:
copy .env.example .env
#    Mac/Linux:
cp .env.example .env
```

Indi `.env` faýlyny Notepad (ýa-da islendik tekst redaktory) bilen açyň we:
- `TELEGRAM_TOKEN=` – BotFather-dan alan tokeniňizi goýuň
- `AI_API_KEY=` – Groq açaryňyzy goýuň

Soňra boty işlediň:
```bash
python bot.py
```

`Bot işledi!` diýen ýazgy çyksa – Telegramda botuňyza giriň, `/start` basyň we ýazyň. 🎉

Boty duruzmak üçin terminalda **Ctrl + C** basyň.

---

## 🌐 3-nji ädim: Serwerde 24/7 işletmek

Kompýuteriňizi öçürseňiz, bot hem durýar. Hemişe işlemegi üçin ony serwere goýmaly.

### Mugt ýa-da arzan serwer wariantlary
- **Oracle Cloud Always Free** – hemişelik mugt serwer (kart bilen tassyklamak gerek, ýöne pul alynmaýar)
- **Google Cloud e2-micro** – mugt derejesi bar
- Islendik arzan VPS (Hetzner, DigitalOcean we ş.m., aýda ~4-5$)

Serweriňizde **Ubuntu** saýlaň.

### Serwere goýmak (Docker bilen – iň aňsat ýoly)
Serwere SSH arkaly giriň we şulary ýazyň:

```bash
# 1. Docker guruň (diňe bir gezek)
curl -fsSL https://get.docker.com | sh

# 2. Kody göçüriň
git clone https://github.com/k9032431-cmd/TelegramAI.git
cd TelegramAI

# 3. Sazlamalary ýazyň
cp .env.example .env
nano .env        # açarlary ýazyň, soňra Ctrl+O, Enter, Ctrl+X

# 4. Boty işlediň
docker compose up -d --build
```

Hemme zat! Bot indi hemişe işleýär, serwer täzeden açylsa-da özi başlar.

### Peýdaly buýruklar
| Buýruk | Näme edýär |
|---|---|
| `docker compose logs -f` | Botuň näme edýänini görmek (çykmak: Ctrl+C) |
| `docker compose restart` | Täzeden başlatmak (`.env` üýtgedeniňizden soň) |
| `docker compose down` | Duruzmak |
| `git pull && docker compose up -d --build` | Kody täzeläp, täzeden işletmek |

---

## ⚙️ Sazlamalar (`.env` faýlynda)

| Ady | Näme | Mysal |
|---|---|---|
| `TELEGRAM_TOKEN` | BotFather tokeni | `7123...:AAH...` |
| `AI_API_KEY` | AI hyzmatynyň açary | `gsk_...` |
| `AI_BASE_URL` | AI hyzmatynyň salgysy | `https://api.groq.com/openai/v1` |
| `AI_MODEL` | Haýsy AI modeli | `llama-3.3-70b-versatile` |
| `SYSTEM_PROMPT` | Botuň häsiýeti, özüni nähili alyp barmaly | `Sen degişmegi gowy görýän kömekçi.` |
| `HISTORY_LIMIT` | Näçe habary ýatda saklasyn | `20` |
| `ALLOWED_USERS` | Diňe şu ID-ler ulanyp bilsin | `123456789,987654321` |

> 💡 Öz Telegram ID-ňizi bilmek üçin **@userinfobot**-a ýazyň.
>
> 💡 Botuňyzy diňe özüňiz ulanjak bolsaňyz, `ALLOWED_USERS` ýazyň – ýogsa başgalar hem siziň mugt limitiňizi harçlap biler.

---

## ❓ Ýygy duş gelýän meseleler

| Mesele | Çözgüdi |
|---|---|
| `TELEGRAM_TOKEN we AI_API_KEY ... ýazylmaly!` | `.env` faýly ýok ýa-da açarlar ýazylmandyr. `.env.example` däl-de, `.env` faýlyny düzediň. |
| `python` tapylmady | Windows-da Python-y "Add to PATH" bilen täzeden guruň. Mac/Linux-da `python3` ýazyp görüň. |
| Bot "AI hyzmatynda ýalňyşlyk" diýýär | Logda (`docker compose logs`) sebäbi ýazylýar. Köplenç açar nädogry ýa-da model ady köne. Täze model adyny AI saýtyndan (meselem console.groq.com/docs/models) alyň. |
| "Mugt limit gutardy" | Mugt hyzmatlarda minutda/günde çäk bar. Biraz garaşyň ýa-da başga hyzmata geçiň. |
| Bot jogap bermeýär | Bot işleýärmi? Terminal ýa-da `docker compose ps` bilen barlaň. Bir token bilen diňe **bir** bot işläp biler. |

---

## 🔒 Howpsuzlyk
- `.env` faýlyny **hiç haçan** GitHub-a goýmaň we hiç kime ibermäň (`.gitignore` ony eýýäm goraýar).
- Token tötänleýin görünse – BotFather-da `/revoke` bilen täzeläň.
