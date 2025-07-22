import os

class Config:
    # Discord
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    GUILD_ID = int(os.getenv('GUILD_ID', 0))
    
    # Admin roles/users
    ADMIN_ROLE_ID = int(os.getenv('ADMIN_ROLE_ID', 0))
    OWNER_ID = int(os.getenv('OWNER_ID', 0))
    
    # Payment APIs
    PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
    PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')
    PAYPAL_SANDBOX = os.getenv('PAYPAL_SANDBOX', 'true').lower() == 'true'
    
    # Crypto settings
    ETH_WALLET_ADDRESS = os.getenv('ETH_WALLET_ADDRESS')
    LTC_WALLET_ADDRESS = os.getenv('LTC_WALLET_ADDRESS')
    
    # CashApp
    CASHAPP_USERNAME = os.getenv('CASHAPP_USERNAME', '$YourCashApp')
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'shop.db')
    
    # Bot settings
    EMBED_COLOR = 0x5865F2  # Discord blurple
    SUCCESS_COLOR = 0x57F287  # Green
    ERROR_COLOR = 0xED4245    # Red
    WARNING_COLOR = 0xFEE75C  # Yellow
    
    # Shop categories
    CATEGORIES = {
        'robux': {
            'name': 'Robux',
            'emoji': '💎',
            'description': 'Roblox currency'
        },
        'nitro': {
            'name': 'Discord Nitro',
            'emoji': '🎮',
            'description': 'Discord premium subscriptions'
        },
        'decorations': {
            'name': 'Decorations',
            'emoji': '🎨',
            'description': 'Custom decorations and accessories'
        }
    }
    
    # Payment methods
    PAYMENT_METHODS = {
        'paypal': {
            'name': 'PayPal',
            'emoji': '💰',
            'enabled': bool(PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET)
        },
        'eth': {
            'name': 'Ethereum',
            'emoji': '⟠',
            'enabled': bool(ETH_WALLET_ADDRESS)
        },
        'ltc': {
            'name': 'Litecoin',
            'emoji': 'Ł',
            'enabled': bool(LTC_WALLET_ADDRESS)
        },
        'cashapp': {
            'name': 'CashApp',
            'emoji': '💵',
            'enabled': bool(CASHAPP_USERNAME)
        }
    }
