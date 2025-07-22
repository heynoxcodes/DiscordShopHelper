# Discord Shop Bot

A Discord bot for selling digital products like Robux, Discord Nitro, and custom decorations with multi-payment support.

## Features

- 🛍️ **Product Catalog**: Browse Robux, Discord Nitro, and decorations
- 💳 **Multiple Payments**: PayPal, Ethereum, Litecoin, CashApp
- 📊 **Admin Dashboard**: Sales analytics, order management, inventory tracking
- 🎫 **Support System**: Built-in customer support tickets
- 📱 **User-Friendly**: Modern slash commands and interactive buttons

## Quick Setup

### 1. Create Discord Bot
1. Go to https://discord.com/developers/applications
2. Create new application → Bot section → Copy token
3. Enable "applications.commands" scope when inviting

### 2. Deploy on Railway (Free)
1. Fork this repository to your GitHub
2. Go to https://railway.app
3. Click "Deploy from GitHub"
4. Select this repository
5. Add environment variable: `DISCORD_TOKEN` = your bot token
6. Deploy!

### 3. Invite Bot to Server
Use the OAuth2 URL generator with:
- Scopes: `bot` + `applications.commands` 
- Permissions: Send Messages, Use Slash Commands, Embed Links

## Commands

### Customer Commands
- `/shop` - Browse all products or filter by category
- `/buy <product_id> [quantity]` - Purchase items
- `/orders` - View your order history
- `/order <order_id>` - Check specific order details

### Admin Commands (requires admin role)
- `/admin` - Dashboard with analytics and quick actions
- `/add_product` - Add new products to catalog
- `/update_stock <product_id> <amount>` - Manage inventory
- `/manage_order <order_id> <status>` - Process customer orders
- `/sales_report [days]` - Generate sales analytics

## Configuration

Set these environment variables:

### Required
- `DISCORD_TOKEN` - Your Discord bot token

### Optional Payment Setup
- `PAYPAL_CLIENT_ID` - PayPal app client ID
- `PAYPAL_CLIENT_SECRET` - PayPal app secret
- `ETH_WALLET_ADDRESS` - Your Ethereum wallet
- `LTC_WALLET_ADDRESS` - Your Litecoin wallet
- `CASHAPP_USERNAME` - Your CashApp tag (e.g., $YourName)

### Optional Admin Setup
- `OWNER_ID` - Your Discord user ID (full admin access)
- `ADMIN_ROLE_ID` - Discord role ID for shop admins

## Easy Updates

### Adding Products
Use the `/add_product` command in Discord - no code changes needed!

### Changing Prices
1. Update in Discord with admin commands, OR
2. Edit the database directly, OR  
3. Modify `bot/config.py` for defaults

### Customizing Categories
Edit `CATEGORIES` in `bot/config.py`:
```python
CATEGORIES = {
    'your_category': {
        'name': 'Display Name',
        'emoji': '🎮',
        'description': 'Category description'
    }
}
```

## Database

Uses SQLite by default (perfect for Railway). Includes:
- Products with stock tracking
- Orders with full lifecycle
- User profiles and purchase history
- Support ticket system
- Inventory logs for admin tracking

## Support

The bot includes a built-in support ticket system. Customers can create tickets directly through Discord when they need help with orders.

## File Structure

```
├── bot/
│   ├── commands/         # Slash commands (shop, admin, orders)
│   ├── database/         # Database models and manager
│   ├── payments/         # Payment method handlers
│   ├── utils/           # Helper functions and embeds
│   └── config.py        # Bot configuration
├── main.py              # Bot setup and initialization  
└── run.py              # Entry point
```

## Contributing

This bot is designed to be easily customizable. Common modifications:
- Add new payment methods in `bot/payments/`
- Create new commands in `bot/commands/`
- Modify embeds in `bot/utils/embeds.py`
- Update categories in `bot/config.py`