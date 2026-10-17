#!/usr/bin/env bash
# Oz AI botuny serwere bir buýruk bilen gurnamak:
#   curl -fsSL https://raw.githubusercontent.com/k9032431-cmd/TelegramAI/ccr-1ece83d6-3yt3px/install.sh | sudo bash
set -euo pipefail

REPO="https://github.com/k9032431-cmd/TelegramAI.git"
BRANCH="ccr-1ece83d6-3yt3px"
DIR="/opt/oz-ai"

say() { printf '\n\033[1;32m==> %s\033[0m\n' "$1"; }
fail() { printf '\n\033[1;31mÝalňyşlyk: %s\033[0m\n' "$1"; exit 1; }
# "curl | bash" bilen işledilende hem klawiaturadan okamak üçin
ask() { local v; read -r -p "$1" v < /dev/tty; printf '%s' "$v" | tr -d '[:space:]'; }

[ "$(id -u)" -eq 0 ] || fail "root bolup işlediň: buýrugyň başyna sudo goşuň."

say "Gerekli programmalar gurnalýar (birnäçe minut gerek bolup biler)..."
if ! command -v git >/dev/null || ! command -v curl >/dev/null; then
  apt-get update -qq && apt-get install -y -qq git curl >/dev/null
fi
if ! command -v docker >/dev/null; then
  curl -fsSL https://get.docker.com | sh >/dev/null
fi

say "Botuň kody alynýar..."
if [ -d "$DIR/.git" ]; then
  git -C "$DIR" fetch -q origin "$BRANCH" && git -C "$DIR" reset -q --hard "origin/$BRANCH"
else
  git clone -q -b "$BRANCH" "$REPO" "$DIR"
fi
cd "$DIR/server"

if [ -f .env ] && [ "$(ask 'Öňki sazlamalar bar. Täzeden girizmekmi? (h/ý): ')" != "h" ]; then
  say "Öňki sazlamalar saklanýar."
else
  say "Sazlamalar"
  while :; do
    TOKEN=$(ask "Telegram tokeni (@BotFather-den): ")
    BOT=$(curl -fsS "https://api.telegram.org/bot$TOKEN/getMe" 2>/dev/null | grep -o '"username":"[^"]*"' | cut -d'"' -f4 || true)
    [ -n "$BOT" ] && { echo "Bot tapyldy: @$BOT"; break; }
    echo "Token nädogry. Gaýtadan göçürip goýuň."
  done
  while :; do
    KEY=$(ask "OpenRouter açary (sk-or-v1-...): ")
    if curl -fsS -o /dev/null https://openrouter.ai/api/v1/key -H "Authorization: Bearer $KEY" 2>/dev/null; then
      echo "Açar işleýär."
      break
    fi
    echo "Açar nädogry. Gaýtadan göçürip goýuň."
  done
  umask 077
  cat > .env <<EOF
TELEGRAM_TOKEN=$TOKEN
AI_PROVIDER=openrouter
AI_API_KEY=$KEY
BOT_NAME=Oz AI
HISTORY_LIMIT=20
EOF
fi

say "Bot işledilýär..."
docker compose up -d --build

say "Taýýar! Telegramda botuňyza /start ýazyň."
cat <<'EOF'
Peýdaly buýruklar:
  cd /opt/oz-ai/server && docker compose logs -f      # loglary görmek (Ctrl+C - çykmak)
  cd /opt/oz-ai/server && docker compose restart      # täzeden başlatmak
  curl -fsSL https://raw.githubusercontent.com/k9032431-cmd/TelegramAI/ccr-1ece83d6-3yt3px/install.sh | sudo bash
                                                     # täzelemek (şol buýruk)
EOF
