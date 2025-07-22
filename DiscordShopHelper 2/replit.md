# Shop Bot - Discord Marketplace Bot

## Overview

This is a Discord bot that creates a marketplace/shop system within Discord servers. Users can browse products, place orders, and make payments through multiple methods including PayPal, cryptocurrency, and CashApp. The bot features admin controls, order management, and a comprehensive database system for tracking products, orders, and payments.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Architecture
- **Framework**: discord.py with slash commands support
- **Command System**: Uses Discord's application commands (slash commands) for modern interaction
- **Modular Design**: Organized into separate cogs for different functionalities (shop, admin, orders)
- **Async/Await Pattern**: Fully asynchronous operation using Python's asyncio

### Database Architecture
- **Database**: SQLite with aiosqlite for async operations
- **Schema**: Three main tables - products, orders, and payments
- **Connection Management**: Connection pooling with proper resource cleanup
- **Data Models**: Centralized schema definition in models.py

### Payment Integration
- **Multi-Payment Support**: PayPal, Ethereum, Litecoin, and CashApp
- **Payment Verification**: Automated for PayPal and crypto, manual for CashApp
- **Price Calculation**: Real-time crypto price fetching from CoinGecko API
- **Transaction Tracking**: Complete payment lifecycle management

## Key Components

### Core Bot Components
- **ShopBot Class**: Main bot instance inheriting from commands.Bot
- **Command Cogs**: Modular command organization
  - Shop commands for product browsing and purchasing
  - Admin commands for management and analytics
  - Order commands for user order history
- **Database Manager**: Centralized database operations
- **Configuration System**: Environment-based configuration management

### Payment Handlers
- **PayPal Handler**: OAuth2 authentication and payment processing
- **Crypto Handler**: Price fetching and payment amount calculation
- **CashApp Handler**: Manual verification system for peer-to-peer payments

### Utility Systems
- **Embed Builder**: Standardized Discord embed creation
- **Logger**: File and console logging with proper formatting
- **Permissions**: Role-based access control for admin functions

## Data Flow

### Product Purchase Flow
1. User browses products via `/shop` command
2. User selects product and payment method via `/buy` command
3. System creates order record in database
4. Payment handler generates payment instructions
5. User completes payment outside Discord
6. System verifies payment (automated or manual)
7. Order status updated and user receives confirmation

### Admin Management Flow
1. Admin accesses dashboard via `/admin` command
2. System displays analytics and pending orders
3. Admin can manage products, orders, and payments
4. All changes are logged and tracked in database

### Database Operations
- **Products**: CRUD operations with stock management
- **Orders**: Order lifecycle tracking with status updates
- **Payments**: Payment verification and reconciliation
- **Analytics**: Sales reporting and business intelligence

## External Dependencies

### APIs and Services
- **Discord API**: Bot functionality and user interaction
- **PayPal API**: Payment processing and verification
- **CoinGecko API**: Real-time cryptocurrency price data
- **CashApp**: Manual payment verification (no API)

### Python Libraries
- **discord.py**: Discord bot framework
- **aiosqlite**: Async SQLite database operations
- **aiohttp**: HTTP client for API requests
- **asyncio**: Asynchronous programming support

### Environment Variables
- Discord bot token and guild configuration
- PayPal API credentials and sandbox settings
- Cryptocurrency wallet addresses
- Admin role and owner ID configuration
- Database path and bot customization settings

## Deployment Strategy

### Environment Setup
- **SQLite Database**: Local file-based storage (shop.db)
- **Logging**: File-based logging (bot.log) with console output
- **Configuration**: Environment variable-based configuration
- **Process Management**: Single process with proper shutdown handling

### Scaling Considerations
- Database can be migrated to PostgreSQL for production
- Payment verification can be enhanced with webhooks
- Multi-server support through guild-specific data isolation
- Horizontal scaling through database connection pooling

### Security Measures
- **Permission System**: Role-based access control
- **Environment Variables**: Sensitive data protection
- **Input Validation**: SQL injection prevention through parameterized queries
- **Error Handling**: Comprehensive exception handling with logging

The bot is designed for easy deployment on platforms like Replit, with all dependencies clearly defined and configuration handled through environment variables. The modular architecture allows for easy feature additions and modifications without affecting core functionality.