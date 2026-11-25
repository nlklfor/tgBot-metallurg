# MTL // PROTOCOL [v.2.026] 🔧

> **[SYSTEM_BOOT]... OK**  
> **[IDENTIFICATION_SUCCESSFUL]**
>
> Telegram bot for the METALLURG™ archive store: order tracking, FAQ and new-drop notifications.

---

## OPERATIONAL COMMANDS 📋

- **[ TRACK_MY_OBJECT ]** / `/track MTL-XXXXXX` — order lookup: status, delivery route, Nova Poshta tracking, items and total. Codes are accepted as `MTL-7K2QPX`, `mtl 7k2qpx` or `7K2QPX`; a bare code sent anytime is looked up too.
- **[ FAQ ]** / `/faq` — delivery, returns, payment
- **[ CONTACT_OPERATOR ]** / `/contact` — the operator's handle
- `/alerts` — turn new-drop alerts on or off (also a button under every alert)
- `/unlink MTL-XXXXXX` — operator only (`OPERATOR_CHAT_IDS`): stop updates for an order so the right customer can link it again

The command menu is set on every start (`setMyCommands`, list in `bot/constants.py`).

**Order updates:** the website's order-confirmed screen links to `t.me/metallurgTm_bot?start=MTL-XXXXXX`. The bot links that chat to the order (`orders.customer_chat_id`, first chat wins) and then messages it whenever the order's status or TTN changes (checked every 60s, `bot/services/order_updates.py`).

The bot also messages everyone who opened it (`bot_users`, keyed by chat id, with or without an @username) when new products appear in the archive: at most once every 12 hours, skipping people who muted alerts or blocked the bot. The last check time lives in `bot_state`, so restarts don't miss or repeat a drop.

## TECHNICAL SPECIFICATIONS 🛠️

| Component | Details |
|-----------|---------|
| **Framework** | [aiogram 3.15](https://github.com/aiogram/aiogram), long polling |
| **Language** | Python 3.10+ (production runs 3.13 on Railway) |
| **Database** | Supabase Postgres via one `asyncpg` pool, as the `metallurg_bot` role (reads orders/products, writes only `bot_users`, `bot_state` and the two Telegram columns on `orders`) |
| **Tracking** | Supabase edge function `nova-poshta-track` (only answers for TTNs that belong to an order) |
| **Parse Mode** | HTML — every value from the DB or Nova Poshta is `html.escape`d |
| **Hosting** | Railway, `Procfile` → `worker: python main.py`, deploys on push to `main` |

## ENVIRONMENT 🔑

Set these in Railway → Variables (or a local `.env`, never committed):

```env
BOT_TOKEN=...            # from @BotFather
DATABASE_URL=postgresql://metallurg_bot.<project-ref>:<password>@<pooler-host>:6543/postgres
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_ANON_KEY=...    # Supabase → Settings → API (public anon key)
SITE_URL=https://metallurg.vercel.app   # optional; change when the domain goes live
OPERATOR_CHAT_IDS=123456789             # optional; chat ids allowed to use /unlink
```

`DATABASE_URL` uses the `metallurg_bot` role (migration `20261125120100_bot_db_role.sql` in the website repo). Set its password once in the Supabase SQL editor (`alter role metallurg_bot with password '...'`) and put the same password here. Your own chat id: send any message to @userinfobot.

Only one process may poll with a given `BOT_TOKEN`: running the bot locally while Railway is up makes Telegram reject one of them.

## LOCAL RUN 🚀

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python3 main.py
```

Tests (no network, no database):

```bash
python3 -m unittest discover -s tests -t .
```

Expected output of `main.py`:
```
✅ Database connected successfully
🚀 Bot is starting...
```

---

## ORDER LOOKUP 🔎

- Route follows `shipping_zone`, exactly like the website:
  - `Ukraine` → `ORDER_ACCEPTED → PACKING → READY_FOR_PICKUP → HANDED_TO_RESIDENT`
  - `International` → `ORDER_ACCEPTED → PROCESSING → IN_TRANSIT_TO_HUB → BORDER_CROSSING → ARRIVED_IN_UKRAINE → DELIVERED_TO_NP`
- Current step = `orders.current_status_index` (set from the admin panel).
- Cancelled orders show `CANCELLED` and no pipeline.
- Customer name and contact are masked (`Nikita S.`, `+380*****4567`).
- Max 8 lookups per chat per 10 minutes (same limit as the site's `track-order`).

### Status map

| `orders.status` | Shown as |
|-----------------|----------|
| `waiting_for_payment` | `[ PENDING_PAYMENT ]` |
| `paid` | `[ PAYMENT_CONFIRMED ]` |
| `processing` | `[ IN_PREPARATION ]` |
| `shipped` | `[ DISPATCHED_TO_HUB ]` |
| `completed` | `[ ARCHIVED_SUCCESSFULLY ]` |
| `cancelled` | `[ CANCELLED ]` |

---

## ARCHITECTURE 🏗️

```
tgBot-metallurg/
├── main.py                  # entry point: DB check, routers, notify loop, polling
├── config.py                # env vars
├── Procfile                 # Railway start command
├── bot/
│   ├── constants.py         # button labels, texts, status map, routes
│   ├── text.py              # pure helpers: code normalising, masks, stepper (tested)
│   ├── handlers/
│   │   ├── start.py         # /start (+ deep link MTL-XXXXXX → order updates), saves the user
│   │   ├── status.py        # order lookup (/track, button, bare codes) — included last
│   │   ├── alerts.py        # /alerts + mute/unmute buttons
│   │   ├── operator.py      # /unlink (OPERATOR_CHAT_IDS only)
│   │   ├── faq.py
│   │   └── contact.py
│   ├── keyboards/           # reply + inline keyboards
│   ├── services/
│   │   ├── order.py         # orders queries (lookup, link, unlink)
│   │   ├── users.py         # bot_users (save, alerts on/off, blocked)
│   │   ├── state.py         # bot_state timestamps
│   │   ├── nova_poshta.py   # calls the nova-poshta-track edge function
│   │   ├── notify.py        # "new items in the archive" broadcast loop
│   │   └── order_updates.py # per-order status/TTN messages to subscribed chats
│   └── states/orders.py     # FSM state for the lookup flow
├── database/connection.py   # asyncpg pool (`async with db() as conn`)
└── tests/test_text.py       # unittest, stdlib only
```

The database schema lives in the website repo: `supabase/schema.sql`.

---

## TROUBLESHOOTING ⚠️

| Symptom | Fix |
|---------|-----|
| `TelegramUnauthorizedError` on start | `BOT_TOKEN` in Railway is wrong or was revoked in @BotFather |
| `TelegramConflictError` | Another copy of the bot is polling with the same token (local run, second Railway environment) |
| `Database connection failed` | Check `DATABASE_URL`; use the Supabase pooler connection string with the `metallurg_bot.<project-ref>` user |
| `permission denied for table …` | The bot role is missing a grant: add it in a new migration in the website repo (see `20261125120100_bot_db_role.sql`) |
| `// SYSTEM_ERROR` in chat | DB unreachable — see Railway logs |
| No Nova Poshta block | Order has no `tracking_number`, or `SUPABASE_URL` / `SUPABASE_ANON_KEY` not set |

---

**[SYSTEM_ONLINE]... READY FOR OPERATIONS** ✅
