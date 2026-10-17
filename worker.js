// Oz AI — Telegram AI boty (Cloudflare Workers üçin, serwer gerek däl)
//
// DIŇE ŞU IKI SETIRI DOLDURYŇ:
const TELEGRAM_TOKEN = "BU_YERE_BOTFATHER_TOKENI";
const AI_API_KEY = "BU_YERE_OPENROUTER_ACHARY";

// Islege görä üýtgedip bilersiňiz:
const BOT_NAME = "Oz AI";
const SYSTEM_PROMPT =
  `Sen ${BOT_NAME} atly peýdaly AI kömekçisiň. ` +
  "Ulanyjy haýsy dilde ýazsa, şol dilde gysga we düşnükli jogap ber.";
const AI_MODEL = "openrouter/free"; // OpenRouter özi işleýän mugt modeli saýlaýar
const AI_URL = "https://openrouter.ai/api/v1/chat/completions";
const HISTORY_LIMIT = 20; // ýatda saklanýan habar sany
const ALLOWED_USERS = []; // boş = hemmä açyk. Mysal: [123456789]

// ---- Mundan aşagy üýtgetmek gerek däl ----

const TELEGRAM_MAX_LEN = 4096;
// KV birikdirilmedik bolsa, ýat diňe wagtlaýyn saklanýar
const memoryFallback = new Map();

export default {
  async fetch(request, env, ctx) {
    const token = env.TELEGRAM_TOKEN || TELEGRAM_TOKEN;
    const url = new URL(request.url);
    const secret = await webhookSecret(token);

    if (request.method === "POST") {
      if (request.headers.get("X-Telegram-Bot-Api-Secret-Token") !== secret) {
        return new Response("forbidden", { status: 403 });
      }
      const update = await request.json();
      // Telegram-a derrew jogap berýäris, AI jogaby fonda taýýarlanýar
      ctx.waitUntil(handleUpdate(update, env, token));
      return new Response("ok");
    }

    if (url.pathname === "/setup") {
      const res = await tg(token, "setWebhook", {
        url: `${url.origin}/`,
        secret_token: secret,
        allowed_updates: ["message"],
        drop_pending_updates: true,
      });
      return new Response(
        res.ok
          ? `Taýýar! ${BOT_NAME} işledi. Indi Telegramda bota /start ýazyň.`
          : `Ýalňyşlyk: ${res.description}\nTELEGRAM_TOKEN dogrumy?`,
        { headers: { "content-type": "text/plain; charset=utf-8" } },
      );
    }

    return new Response(
      `${BOT_NAME} işleýär. Botu birikdirmek üçin şu salgynyň soňuna /setup goşup açyň.`,
      { headers: { "content-type": "text/plain; charset=utf-8" } },
    );
  },
};

async function handleUpdate(update, env, token) {
  const msg = update.message;
  if (!msg || typeof msg.text !== "string") return;
  const chatId = msg.chat.id;
  const text = msg.text.trim();
  const reply = (t) => tg(token, "sendMessage", { chat_id: chatId, text: t });

  if (text.startsWith("/start")) {
    return reply(
      `Salam! Men ${BOT_NAME}. Maňa islän soragyňy ýaz.\n\n` +
        "/new - täze söhbet başlat\n/id - Telegram ID-ňi görkez",
    );
  }
  if (text.startsWith("/id")) return reply(`Seniň ID-ň: ${msg.from.id}`);
  if (text.startsWith("/new")) {
    await saveHistory(env, chatId, []);
    return reply("Täze söhbet başlandy.");
  }
  if (ALLOWED_USERS.length && !ALLOWED_USERS.includes(msg.from.id)) {
    return reply("Bagyşla, bu bot diňe rugsat berlen ulanyjylar üçin.");
  }

  await tg(token, "sendChatAction", { chat_id: chatId, action: "typing" });

  const history = await loadHistory(env, chatId);
  const messages = [
    { role: "system", content: SYSTEM_PROMPT },
    ...history,
    { role: "user", content: text },
  ];

  let answer;
  try {
    answer = await askAI(env.AI_API_KEY || AI_API_KEY, messages);
  } catch (err) {
    console.log("AI ýalňyşlygy:", err.message);
    return reply("Bagyşla, AI häzir jogap berip bilmedi. Birazdan gaýtadan synanyş.");
  }

  history.push({ role: "user", content: text }, { role: "assistant", content: answer });
  await saveHistory(env, chatId, history.slice(-HISTORY_LIMIT));

  for (let i = 0; i < answer.length; i += TELEGRAM_MAX_LEN) {
    await reply(answer.slice(i, i + TELEGRAM_MAX_LEN));
  }
}

async function askAI(apiKey, messages) {
  const res = await fetch(AI_URL, {
    method: "POST",
    headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" },
    body: JSON.stringify({ model: AI_MODEL, messages }),
    signal: AbortSignal.timeout(25000),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(JSON.stringify(data.error || data));
  return (data.choices?.[0]?.message?.content || "").trim() || "...";
}

async function loadHistory(env, chatId) {
  if (env.MEMORY) return (await env.MEMORY.get(`h:${chatId}`, "json")) || [];
  return [...(memoryFallback.get(chatId) || [])];
}

async function saveHistory(env, chatId, history) {
  if (env.MEMORY) return env.MEMORY.put(`h:${chatId}`, JSON.stringify(history));
  memoryFallback.set(chatId, history);
}

async function tg(token, method, body) {
  const res = await fetch(`https://api.telegram.org/bot${token}/${method}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return res.json();
}

// Diňe Telegram-yň özi bota habar iberip bilsin diýip gizlin açar
async function webhookSecret(token) {
  const hash = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(token));
  return [...new Uint8Array(hash)].map((b) => b.toString(16).padStart(2, "0")).join("").slice(0, 48);
}
