# =============================================================
#  Telegram AI bot
#  Bu fayl botyň "beýnisi". Ol Telegramdan habar alýar,
#  ony mugt AI hyzmatyna (Groq / OpenRouter / Gemini) iberýär
#  we jogaby yzyna ulanyja gaýtarýar.
# =============================================================

import logging
import os
from collections import defaultdict, deque

import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# --- 1. Sazlamalary (.env faýlyndan) okaýarys -----------------
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AI_API_KEY = os.getenv("AI_API_KEY")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.groq.com/openai/v1")
AI_MODEL = os.getenv("AI_MODEL", "llama-3.3-70b-versatile")
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "Sen peýdaly we dostlukly kömekçi. Ulanyjy haýsy dilde ýazsa, şol dilde jogap ber.",
)
# Bot her ulanyjynyň näçe soňky habaryny ýatda saklasyn
HISTORY_LIMIT = int(os.getenv("HISTORY_LIMIT", "20"))
# Diňe şu ulanyjylar ulanyp bilsin (boş bolsa – hemmeler)
ALLOWED_USERS = {
    int(x) for x in os.getenv("ALLOWED_USERS", "").replace(" ", "").split(",") if x
}

if not TELEGRAM_TOKEN or not AI_API_KEY:
    raise SystemExit(
        "TELEGRAM_TOKEN we AI_API_KEY .env faýlynda ýazylmaly! README.md-ä serediň."
    )

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO
)
# httpx her soragy logda görkezmesin (token görünmez ýaly)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("bot")

# --- 2. Ýat (gürrüňiň taryhy) ---------------------------------
# Her ulanyjy üçin aýratyn sanaw. deque(maxlen=...) köne
# habarlary özi pozýar, şonuň üçin ýat dolup galmaýar.
history: dict[int, deque] = defaultdict(lambda: deque(maxlen=HISTORY_LIMIT))

# Telegram bir habarda iň köp 4096 harp kabul edýär
TELEGRAM_LIMIT = 4096


# --- 3. AI-dan jogap almak ------------------------------------
async def ask_ai(user_id: int, text: str) -> str:
    history[user_id].append({"role": "user", "content": text})
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, *history[user_id]]

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{AI_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {AI_API_KEY}"},
            json={"model": AI_MODEL, "messages": messages},
        )
    response.raise_for_status()
    answer = response.json()["choices"][0]["message"]["content"].strip()

    history[user_id].append({"role": "assistant", "content": answer})
    return answer


def is_allowed(update: Update) -> bool:
    return not ALLOWED_USERS or update.effective_user.id in ALLOWED_USERS


# --- 4. Buýruklar (/start, /reset, /help) ---------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Salam! 👋 Men AI kömekçi. Maňa islän soragyňy ýaz.\n\n"
        "/reset – gürrüňi täzeden başlamak\n"
        "/help – kömek"
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    history.pop(update.effective_user.id, None)
    await update.message.reply_text("🧹 Ýat arassalandy. Täzeden başlap bileris!")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Diňe soragyňy ýaz – men jogap bererin.\n"
        "Men soňky habarlarymyzy ýatda saklaýaryn.\n"
        "/reset – ýady arassalamak"
    )


# --- 5. Adaty habarlar ----------------------------------------
async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        await update.message.reply_text("⛔ Bu bot diňe rugsat berlen adamlar üçin.")
        return

    user_id = update.effective_user.id
    # "ýazýar..." diýen ýazgyny görkezýäris
    await context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)

    try:
        answer = await ask_ai(user_id, update.message.text)
    except httpx.HTTPStatusError as e:
        # Şowsuz soragy taryhdan aýyrýarys
        if history[user_id]:
            history[user_id].pop()
        log.error("AI ýalňyşlyk %s: %s", e.response.status_code, e.response.text[:300])
        if e.response.status_code == 429:
            await update.message.reply_text("⏳ Mugt limit gutardy, birazdan gaýtadan synanyş.")
        else:
            await update.message.reply_text("😔 AI hyzmatynda ýalňyşlyk boldy. Soňrak synanyş.")
        return
    except Exception:
        if history[user_id]:
            history[user_id].pop()
        log.exception("Garaşylmadyk ýalňyşlyk")
        await update.message.reply_text("😔 Bir zat ýalňyş gitdi. Soňrak synanyş.")
        return

    # Uzyn jogaby birnäçe bölege bölüp iberýäris
    for i in range(0, len(answer), TELEGRAM_LIMIT):
        await update.message.reply_text(answer[i : i + TELEGRAM_LIMIT])


# --- 6. Boty işe girizmek -------------------------------------
def main() -> None:
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    log.info("Bot işledi! Model: %s", AI_MODEL)
    app.run_polling()


if __name__ == "__main__":
    main()
