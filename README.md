# Telegram Order Tracking Bot 🤖

A professional Telegram bot for managing product orders and tracking order status. Built with aiogram 3.x and SQLAlchemy for reliable order management.

## Features ✨

- 📦 **Product Ordering**: Users can browse and order products
- 📍 **Order Tracking**: Real-time order status tracking with emoji indicators
- 🛠️ **Admin Panel**: Full admin commands for order management and user notifications
- 🔐 **Admin Authentication**: Only authorized admins can access admin commands
- 💾 **Database**: SQLite with async SQLAlchemy ORM
- 🔄 **FSM States**: Finite State Machine for managing order flows
- 📝 **Logging**: Comprehensive logging for debugging and monitoring

## Tech Stack 🛠️

- **Framework**: [aiogram 3.x](https://github.com/aiogram/aiogram) - Telegram Bot API
- **Database**: SQLite + [SQLAlchemy 2.x](https://www.sqlalchemy.org/) (async)
- **Driver**: aiosqlite for async database operations
- **Language**: Python 3.9+
- **Architecture**: Handlers, Repositories, Models with FSM states

## Installation 📥

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd tgBot-metallurg
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   - Copy `.env.example` to `.env`
   - Add your Telegram Bot API token
   - Add admin user IDs (comma-separated)
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

5. **Run the bot**
   ```bash
   python3 main.py
   ```

## Configuration 🔧

### .env File

```env
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here

# Admin Configuration
# Comma-separated list of admin user IDs
ADMINS=123456789,987654321

# Database (optional, defaults to metallurg_bot.db)
DATABASE_URL=sqlite+aiosqlite:///metallurg_bot.db
```

### Get Your Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Create a new bot: `/newbot`
3. Copy the token provided

### Find Your User ID

1. Open Telegram and search for [@userinfobot](https://t.me/userinfobot)
2. Send any message to get your user ID

## User Commands 👤

Available commands for regular users:

### `/start`
Main menu with product catalog access
- Shows welcome message
- Displays start keyboard with options

### `/status`
Check order status by tracking code
- Enter tracking code when prompted
- Receive detailed order information with current status
- Use inline button to quickly check status again

### Status Indicators 📊
Orders display with colored circle emojis:
- 🔵 **CREATED** - Order has been created
- 🟡 **PAID** - Payment received
- 🟠 **IN_TRANSIT** - Order is being delivered
- 🟢 **DELIVERED** - Order successfully delivered
- 🔴 **CANCELLED** - Order has been cancelled

## Admin Commands 🛠️

**Note**: Only users in the `ADMINS` list can execute these commands.

### `/admin_help`
Display all available admin commands
- Shows command list with descriptions
- Lists all available order statuses

### `/orders`
Display the last 20 orders in the system
- Shows order tracking codes
- Displays user IDs
- Shows current order status
- Shows order creation date and time

**Format**:
```
📦 ПОСЛЕДНИЕ 20 ЗАКАЗОВ
========================================

1. 🔑 Трек-код: TEST123456
   👤 ID пользователя: 748959905
   📍 Статус: 🔵 CREATED
   ⏰ Дата: 06.02.2026 14:30
```

### `/order_info [tracking_code]`
Get detailed information about a specific order

**Usage**:
```
/order_info TEST123456
```

**Or** - Execute command and enter tracking code when prompted

**Returns**:
- Tracking code
- User ID
- Product ID
- Current status
- Order creation date and time

### `/set_status [tracking_code] [status]`
Change the status of an order

**Usage**:
```
/set_status TEST123456 IN_TRANSIT
```

**Or** - Execute command and follow prompts:
1. Enter tracking code
2. Select new status from available options: `CREATED`, `PAID`, `IN_TRANSIT`, `DELIVERED`, `CANCELLED`

**Available Statuses**:
- `CREATED` - Initial status
- `PAID` - After payment received
- `IN_TRANSIT` - When order ships
- `DELIVERED` - Upon successful delivery
- `CANCELLED` - If order is cancelled

### `/notify_user [tracking_code]`
Send a notification message to a user about their order

**Usage**:
```
/notify_user TEST123456
```

**Or** - Execute command and follow prompts:
1. Enter tracking code
2. Type the message to send to user

**Example message**:
```
Your order is on the way! 🚚
Estimated delivery: 2-3 days
```

## Project Structure 📁

```
tgBot-metallurg/
├── main.py                 # Bot entry point and initialization
├── config.py              # Configuration settings
├── database.py            # Database connection and session management
│
├── models/                # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── base.py           # Base model class
│   ├── enum.py           # Order status enum with emojis
│   ├── product.py        # Product model
│   └── order.py          # Order model
│
├── repositories/          # Data access layer
│   ├── __init__.py
│   ├── product.py        # Product repository methods
│   └── order.py          # Order repository methods
│
├── handlers/             # Message and callback handlers
│   ├── __init__.py
│   ├── start.py         # /start command handler
│   ├── order.py         # Order creation handlers
│   ├── status.py        # /status command handler
│   └── admin.py         # Admin command handlers
│
├── keyboards/            # Telegram inline and reply keyboards
│   ├── __init__.py
│   ├── start.py         # Start menu keyboard
│   ├── order.py         # Order confirmation keyboard
│   └── status.py        # Status check keyboard
│
├── states/              # FSM state definitions
│   ├── __init__.py
│   └── order.py         # Order flow states
│
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore rules
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Database Schema 🗄️

### Products Table
```sql
- id (String, Primary Key)
- title (String)
- description (String)
- price (Float)
- is_active (Boolean)
```

### Orders Table
```sql
- id (UUID, Primary Key)
- tracking_code (String, Unique)
- user_id (Integer)
- product_id (String, Foreign Key)
- status (String) - Enum: CREATED, PAID, IN_TRANSIT, DELIVERED, CANCELLED
- created_at (DateTime)
```

## Example Workflow 🔄

### Creating an Order
1. User sends `/start`
2. User selects a product from the keyboard
3. Bot shows product details and confirmation button
4. User clicks "Confirm Order"
5. Bot creates order and returns tracking code

### Checking Order Status
1. User sends `/status`
2. Bot asks for tracking code
3. User enters tracking code
4. Bot displays order status with all details

### Admin Updating Order
1. Admin sends `/set_status`
2. Admin enters tracking code
3. Admin selects new status
4. Bot confirms status update
5. Order status is updated in database

## Logging 📋

Logs are configured with:
- **Level**: INFO (use DEBUG for more verbose logging)
- **Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **File**: Logs appear in terminal and can be saved to file

Key logged events:
- User command execution
- Product lookups
- Order creation
- Order status updates
- Admin actions
- Errors with full tracebacks

## Testing 🧪

### Test with Provided Data
The bot includes test data creation on startup:
- **Test Product ID**: `test_metal_001`
- **Test Tracking Code**: `TEST123456`

### Manual Testing
1. Send `/start test_metal_001` to create order
2. Send `/status` and enter `TEST123456` to check status
3. As admin, send `/orders` to see all orders
4. As admin, send `/set_status TEST123456 IN_TRANSIT` to update status

## Error Handling ⚠️

The bot includes comprehensive error handling:
- ✅ Database errors handled gracefully
- ✅ Invalid tracking codes return helpful messages
- ✅ Admin authorization verified before sensitive operations
- ✅ FSM state management prevents invalid state transitions
- ✅ All exceptions logged with full tracebacks

## Troubleshooting 🔍

### Bot doesn't start
```bash
# Check Python version
python3 --version  # Should be 3.9+

# Check dependencies
pip list | grep -E "aiogram|sqlalchemy|aiosqlite"

# Check .env file
cat .env  # Ensure BOT_TOKEN is set
```

### Command not responding
- Verify bot token is correct in `.env`
- Check bot is running: `python3 main.py`
- Try `/start` command first to initialize
- Check logs for error messages

### Database errors
```bash
# Reset database (WARNING: deletes all data)
rm metallurg_bot.db
python3 main.py  # Will create fresh database
```

### Admin commands not working
- Verify your user ID is in `ADMINS` list in `.env`
- Restart bot after changing `.env`
- Check logs for authorization errors

## Dependencies 📦

See `requirements.txt` for complete list:
- aiogram - Telegram Bot API framework
- sqlalchemy - ORM for database
- aiosqlite - Async SQLite driver
- greenlet - Required for async SQLAlchemy

## Contributing 🤝

1. Create a new branch for your feature
2. Make changes and test thoroughly
3. Commit with clear messages
4. Push and create a pull request

## License 📄

This project is private and proprietary.

## Support 💬

For issues or questions:
1. Check the troubleshooting section above
2. Review logs for error details
3. Check FSM states in `states/order.py`

## Changelog 📝

### Version 1.0.0 (Initial Release)
- ✅ Product ordering system
- ✅ Order status tracking
- ✅ Admin command panel
- ✅ FSM state management
- ✅ Database persistence
- ✅ Comprehensive logging
- ✅ Error handling

---

**Created with ❤️ for reliable order management**
