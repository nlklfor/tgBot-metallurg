# MTL // PROTOCOL [v.2.026] 🔧

> **[SYSTEM_BOOT]... OK**  
> **[IDENTIFICATION_SUCCESSFUL]**
>
> Telegram bot for the METALLURG™ archive store: order tracking, FAQ and new-drop notifications.

---

## OPERATIONAL COMMANDS 📋

- **[ TRACK_MY_OBJECT ]** — order lookup by code (`MTL-XXXXXX`): status, delivery route, Nova Poshta tracking, items and total
- **[ FAQ ]** — delivery, returns, payment
- **[ CONTACT_OPERATOR ]** — link to the manager

The bot also pings everyone who pressed /start (users with a Telegram @username) when new products appear in the archive (at most once every 12 hours).

## TECHNICAL SPECIFICATIONS 🛠️

| Component | Details |
|-----------|---------|
| **Framework** | [aiogram 3.15](https://github.com/aiogram/aiogram), long polling |
| **Language** | Python 3.10+ (production runs 3.13 on Railway) |
| **Database** | Supabase Postgres via `asyncpg` (direct connection, read-only use except `bot_users`) |
| **Tracking** | Supabase edge function `nova-poshta-track` (only answers for TTNs that belong to an order) |
| **Parse Mode** | HTML — every value from the DB or Nova Poshta is `html.escape`d |
| **Hosting** | Railway, `Procfile` → `worker: python main.py`, deploys on push to `main` |

## ENVIRONMENT 🔑

Set these in Railway → Variables (or a local `.env`, never committed):

```env
BOT_TOKEN=...            # from @BotFather
DATABASE_URL=postgresql://...   # Supabase → Connect → connection string (pooler)
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_ANON_KEY=...    # Supabase → Settings → API (public anon key)
```

Only one process may poll with a given `BOT_TOKEN`: running the bot locally while Railway is up makes Telegram reject one of them.

## LOCAL RUN 🚀

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python3 main.py
```

Expected output:
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
│   ├── handlers/
│   │   ├── start.py         # /start, saves the user to bot_users
│   │   ├── status.py        # order lookup
│   │   ├── faq.py
│   │   └── contact.py
│   ├── keyboards/           # reply + inline keyboards
│   ├── services/
│   │   ├── order.py         # orders / bot_users queries
│   │   ├── nova_poshta.py   # calls the nova-poshta-track edge function
│   │   └── notify.py        # "new items in the archive" broadcast loop
│   └── states/orders.py     # FSM state for the lookup flow
└── database/connection.py   # asyncpg connection
```

The database schema lives in the website repo: `supabase/schema.sql`.

---

## TROUBLESHOOTING ⚠️

| Symptom | Fix |
|---------|-----|
| `TelegramUnauthorizedError` on start | `BOT_TOKEN` in Railway is wrong or was revoked in @BotFather |
| `TelegramConflictError` | Another copy of the bot is polling with the same token (local run, second Railway environment) |
| `Database connection failed` | Check `DATABASE_URL`; use the Supabase pooler connection string |
| `// SYSTEM_ERROR` in chat | DB unreachable — see Railway logs |
| No Nova Poshta block | Order has no `tracking_number`, or `SUPABASE_URL` / `SUPABASE_ANON_KEY` not set |

---

**[SYSTEM_ONLINE]... READY FOR OPERATIONS** ✅
