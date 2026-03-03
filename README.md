# MTL // PROTOCOL [v.2.026] 🔧

> **[SYSTEM_BOOT]... OK**  
> **[IDENTIFICATION_SUCCESSFUL]**
>
> Enterprise-grade Telegram bot for metallurgy order tracking and management. Real-time status updates, secure authentication, and seamless user experience.

---

## OPERATIONAL COMMANDS 📋

- **< TRACK_ORDER_STATUS >** - Real-time order tracking with status indicators
- **< FAQ >** - Comprehensive knowledge base (Доставка, Видмова та Повернення, Методи Оплати)
- **< CONTACT_MANAGER >** - Direct communication channel with support team
- **< BACK_TO_MENU >** - Navigation control across all sections

## TECHNICAL SPECIFICATIONS 🛠️

| Component | Details |
|-----------|---------|
| **Framework** | [aiogram 3.x](https://github.com/aiogram/aiogram) |
| **Language** | Python 3.9+ |
| **Architecture** | Handlers + FSM States + Service Layer |
| **Parse Mode** | HTML |

## SYSTEM REQUIREMENTS 📦

- Python 3.9 or higher
- pip / Poetry (Python package manager)
- Virtual environment (recommended)

## INSTALLATION PROTOCOL 🚀

### 1️⃣ Clone Repository
```bash
git clone https://github.com/your-org/tgBot-metallurg.git
cd tgBot-metallurg
```

### 2️⃣ Initialize Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Environment Configuration
Create `.env` file in project root:
```env
BOT_TOKEN=your_telegram_bot_token_here
DATABASE_URL=sqlite+aiosqlite:///./db.sqlite3
ADMINS=admin_id_1,admin_id_2
```
### 5️⃣ Launch Service
```bash
python3 main.py
```

Expected output:
```
✅ Database connected successfully
🚀 Bot is starting...
```

---

## USER INTERFACE 🖥️

### OPERATIONAL MODES

#### < TRACK_ORDER_STATUS >
Query order status by tracking code
- **Input**: Tracking code in format `XXXXXXX`
- **Output**: Real-time status with indicator
- **Status Map**:
  - `[PENDING_PAYMENT]` - Awaiting payment confirmation
  - `[PAYMENT_CONFIRMED]` - Transaction processed
  - `[IN_PREPARATION]` - Order assembly in progress
  - `[DISPATCHED_TO_HUB]` - In transit to destination
  - `[ARCHIVED_SUCCESSFULLY]` - Delivery complete

#### < FAQ >
Knowledge base & Protocol Documentation
- **[01] ДОСТАВКА** - Express delivery via Нова Пошта (1-3 business days)
- **[02] ОБМІН ТА ПОВЕРНЕННЯ** - 14-day return window (pristine condition)
- **[03] ОПЛАТА** - Secure card transactions or cash-on-delivery

#### < CONTACT_MANAGER >
Direct communication with support team
- Accessible during business hours
- Real-time message routing

#### < BACK_TO_MENU >
Navigation control
- Return to main menu from any section

---

## ARCHITECTURE 🏗️

```
tgBot-metallurg/
├── main.py                      # Service entry point
├── config.py                    # Configuration loader
│
├── bot/
│   ├── __init__.py
│   ├── constants.py            # System constants & status map
│   │
│   ├── handlers/               # Command processors
│   │   ├── start.py           # [SYSTEM_BOOT] initialization
│   │   ├── status.py          # Status query handler
│   │   ├── faq.py             # Knowledge base handler
│   │   ├── contact.py         # Communication handler
│   │   └── navigation.py      # Menu navigation
│   │
│   ├── keyboards/              # UI component definitions
│   │   └── main.py            # Main keyboard layout
│   │
│   ├── services/               # Business logic layer
│   │   └── order.py           # Order operations
│   │
│   └── states/                 # FSM (Finite State Machine)
│       └── orders.py          # Order flow states
│
├── database/
│   └── connection.py           # Async SQLite connection
│
├── requirements.txt            # Dependency manifest
└── README.md                   # This documentation
```

---

```

### Obtaining Credentials

**User ID**:
1. Open Telegram → Search [@userinfobot](https://t.me/userinfobot)
2. Send any message
3. Copy displayed User ID to ADMINS

---

## DATABASE SCHEMA 💾

### Orders Table
```supabase
tracking_code     | STRING (Primary Key)
user_id          | INTEGER
status           | STRING (ForeignKey: StatusMap)
created_at       | DATETIME
updated_at       | DATETIME
```

### Status Registry
Reference: [bot/constants.py](bot/constants.py#L10)

---

## OPERATIONAL WORKFLOW 🔄

### Order Status Check Flow
```
User sends < TRACK_ORDER_STATUS >
        ↓
System prompts: "Enter tracking code"
        ↓
User submits: [CODE]
        ↓
Query database for matching order
        ↓
Format response with current status
        ↓
Return formatted message to user
```

---

## ERROR HANDLING & RECOVERY ⚠️

| Issue | Resolution |
|-------|-----------|
| **Bot offline** | Verify `BOT_TOKEN` in `.env` / Restart service |
| **DB connection failed** | Check `DATABASE_URL` format / Verify file permissions |
| **Command unresponsive** | Check bot process: `ps aux \| grep main.py` |
| **Invalid tracking code** | Confirm code format / Check order exists |

### Debug Mode
```bash
# Enable verbose logging
python3 -c "import logging; logging.basicConfig(level=logging.DEBUG)" && python3 main.py
```

---

## DEPLOYMENT NOTES 📋

- **Python**: 3.9+ required
- **Runtime**: Async event-driven
- **Memory**: ~150MB baseline
- **Parse Mode**: HTML for rich formatting
- **Timezone**: UTC (configurable via environment)

---

## STATUS REFERENCE 📊

| Code | Display | Description |
|------|---------|-------------|
| `waiting_for_payment` | `[PENDING_PAYMENT]` | Payment required |
| `paid` | `[PAYMENT_CONFIRMED]` | Transaction complete |
| `processing` | `[IN_PREPARATION]` | Assembly stage |
| `shipped` | `[DISPATCHED_TO_HUB]` | In transportation |
| `completed` | `[ARCHIVED_SUCCESSFULLY]` | Delivered |

---

## PROJECT METADATA 📌

- **Version**: v.2.026
- **Protocol**: MTL // PROTOCOL
- **Status**: OPERATIONAL
- **Last Updated**: March 2026
- **Language**: Python 3.9+
- **License**: Private & Proprietary

---

**[SYSTEM_ONLINE]... READY FOR OPERATIONS** ✅
