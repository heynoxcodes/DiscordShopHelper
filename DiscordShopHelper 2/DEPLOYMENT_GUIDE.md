# Auto-Deployment Setup Guide

## 🚀 One-Time Setup (5 minutes)

### Step 1: Get Your Code on GitHub
1. Go to https://github.com and create a new repository
2. Name it something like "discord-shop-bot"
3. Make it **private** (recommended for business bots)
4. **Don't** initialize with README (we already have files)

### Step 2: Upload from Replit to GitHub
1. In Replit, click the **Version Control** tab (left sidebar)
2. Click **"Create a Git repository"** 
3. Click **"Connect to GitHub"**
4. Select your new repository
5. Click **"Push to GitHub"** - this uploads all your files

### Step 3: Deploy on Railway
1. Go to https://railway.app and sign up
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Connect your GitHub account if needed
4. Select your discord-shop-bot repository
5. Railway automatically detects it's a Python project

### Step 4: Add Environment Variables
In Railway dashboard:
1. Go to **Variables** tab
2. Add: `DISCORD_TOKEN` = (your Discord bot token)
3. Optional: Add payment variables if you want:
   - `PAYPAL_CLIENT_ID`
   - `PAYPAL_CLIENT_SECRET`
   - `ETH_WALLET_ADDRESS`
   - `LTC_WALLET_ADDRESS`
   - `CASHAPP_USERNAME`

### Step 5: Deploy!
1. Click **"Deploy"**
2. Wait 2-3 minutes for first deployment
3. Your bot is now online 24/7!

## ✨ How Auto-Updates Work

### Option 1: Discord Commands (Most Changes)
- `/add_product` - Add new items to sell
- `/update_stock` - Change inventory amounts
- `/manage_order` - Process customer orders
- No coding required!

### Option 2: Code Changes (When Needed)
1. **Make changes in Replit** (this page)
2. **Click Version Control** → **"Push to GitHub"**
3. **Railway automatically detects** the changes
4. **Railway automatically redeploys** (2-3 minutes)
5. **Your bot updates** with zero downtime!

### Option 3: Edit Directly on Railway
1. Go to Railway dashboard
2. Click **"Code"** tab
3. Edit files directly in browser
4. Click **"Deploy"** - instant update!

## 🎯 What This Means For You

### Daily Operations
- **Add products**: Use `/add_product` in Discord
- **Check sales**: Use `/admin` dashboard in Discord
- **Process orders**: Use `/manage_order` in Discord
- **Update stock**: Use `/update_stock` in Discord

### Code Updates (Rare)
- **Edit once** in Replit or Railway
- **Push to GitHub** (one click)
- **Auto-deploys everywhere**
- **No manual re-uploading**

### Benefits
- ✅ Bot runs 24/7 even when you sleep
- ✅ Customers can buy anytime
- ✅ All data persists forever
- ✅ Easy updates without technical hassle
- ✅ Professional reliability
- ✅ Free hosting (Railway's free tier)

## 🔧 Future Customizations

Want to change something? Edit these files:

### Business Settings
- `bot/config.py` - Categories, colors, payment methods
- Discord commands - Add products directly in chat

### Advanced Features
- `bot/commands/` - Add new slash commands
- `bot/payments/` - Add new payment methods
- `bot/utils/embeds.py` - Change message appearance

## 💡 Pro Tips

1. **Test locally first**: Make changes in Replit, test with your bot, then push to production
2. **Backup important data**: Railway keeps your database, but export important orders periodically
3. **Monitor your bot**: Check Railway dashboard occasionally to ensure everything's running
4. **Use Discord for 90% of tasks**: Most shop management happens through Discord commands

Your bot is now a professional, always-online business tool!