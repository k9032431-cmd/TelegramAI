"""Telegram AI bot: mugt AI API (Groq, Gemini, OpenRouter) bilen işleýär."""

import logging
import os
from collections import defaultdict, deque

from dotenv import load_dotenv
from openai import AsyncOpenAI, AuthenticationError
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

# Mugt AI üpjün edijiler. Hemmesi OpenAI-a meňzeş API ulanýar.
PROVIDERS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.3-70b-versatile",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model": "gemini-2.5-flash",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        # Mugt modeller käte dolup galýar, şonda nobatdaky model synalýar
        "model": "nvidia/nemotron-3-super-120b-a12b:free,"
        "google/gemma-4-31b-it:free,"
        "nvidia/nemotron-3-ultra-550b-a55b:free,"
        "openrouter/free",
    },
}

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
AI_API_KEY = os.environ["AI_API_KEY"]
AI_PROVIDER = os.getenv("AI_PROVIDER", "openrouter").lower()
provider = PROVIDERS.get(AI_PROVIDER, PROVIDERS["openrouter"])
AI_BASE_URL = os.getenv("AI_BASE_URL") or provider["base_url"]
# Birnäçe model otur bilen ýazylyp bilner: "model1,model2"
AI_MODELS = [m.strip() for m in (os.getenv("AI_MODEL") or provider["model"]).split(",") if m.strip()]
BOT_NAME = os.getenv("BOT_NAME", "Oz AI")
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    f"Sen {BOT_NAME} atly peýdaly AI kömekçisiň. "
    "Ulanyjy haýsy dilde ýazsa, şol dilde gysga we düşnükli jogap ber.",
)
# Her söhbetde ýatda saklanýan habarlaryň sany
HISTORY_LIMIT = int(os.getenv("HISTORY_LIMIT", "20"))
# Boş goýulsa, bot hemmä jogap berýär. Mysal: "123456789,987654321"
ALLOWED_USERS = {
    int(x) for x in os.getenv("ALLOWED_USERS", "").replace(" ", "").split(",") if x
}

TELEGRAM_MAX_LEN = 4096

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO
)
for name in ("httpx", "httpx2"):
    logging.getLogger(name).setLevel(logging.WARNING)
log = logging.getLogger("bot")

client = AsyncOpenAI(api_key=AI_API_KEY, base_url=AI_BASE_URL, timeout=60, max_retries=0)
history: dict[int, deque] = defaultdict(lambda: deque(maxlen=HISTORY_LIMIT))


def is_allowed(update: Update) -> bool:
    return not ALLOWED_USERS or update.effective_user.id in ALLOWED_USERS


async def ask_ai(messages: list[dict]) -> str | None:
    for model in AI_MODELS:
        try:
            response = await client.chat.completions.create(
                model=model, messages=messages
            )
            answer = (response.choices[0].message.content or "").strip()
            if answer:
                return answer
            log.warning("%s: boş jogap", model)
        except AuthenticationError:
            log.error("AI_API_KEY nädogry")
            return None
        except Exception as err:
            log.warning("%s: %s", model, err)
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"Salam! Men {BOT_NAME}. Maňa islän soragyňy ýaz.\n\n"
        "/new - täze söhbet başlat\n"
        "/help - kömek\n"
        "/id - Telegram ID-ňi görkez"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Maňa haýsy dilde isleseň ýaz, men jogap bererin.\n"
        "Men soňky habarlaryňy ýatda saklaýaryn.\n"
        "/new - ýatdakylary arassala we täzeden başla."
    )


async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    history.pop(update.effective_chat.id, None)
    await update.message.reply_text("Täze söhbet başlandy.")


async def show_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Seniň ID-ň: {update.effective_user.id}")


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        await update.message.reply_text("Bagyşla, bu bot diňe rugsat berlen ulanyjylar üçin.")
        return

    chat_id = update.effective_chat.id
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += list(history[chat_id])
    messages.append({"role": "user", "content": user_text})

    answer = await ask_ai(messages)
    if answer is None:
        await update.message.reply_text(
            "Bagyşla, AI häzir jogap berip bilmedi. Birazdan gaýtadan synanyş."
        )
        return

    history[chat_id].append({"role": "user", "content": user_text})
    history[chat_id].append({"role": "assistant", "content": answer})

    # Telegram bir habarda 4096 simwoldan köp kabul etmeýär
    for i in range(0, len(answer), TELEGRAM_MAX_LEN):
        await update.message.reply_text(answer[i : i + TELEGRAM_MAX_LEN])


def main() -> None:
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("new", new_chat))
    app.add_handler(CommandHandler("id", show_id))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    log.info("%s işledi: provider=%s model=%s", BOT_NAME, AI_PROVIDER, AI_MODELS[0])
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
