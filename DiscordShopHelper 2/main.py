import discord
from discord.ext import commands
import asyncio
import os
from bot.config import Config
from bot.database.manager import DatabaseManager
from bot.utils.logger import setup_logger

# Setup logging
logger = setup_logger()

class ShopBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        # Only enable what we need for slash commands
        intents.guilds = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        self.db = DatabaseManager()
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        try:
            # Initialize database
            await self.db.initialize()
            
            # Add sample products if database is empty
            await self.add_sample_products()
            
            # Load cogs
            await self.load_extension('bot.commands.shop')
            await self.load_extension('bot.commands.admin')
            await self.load_extension('bot.commands.orders')
            
            # Sync slash commands
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
            
        except Exception as e:
            logger.error(f"Setup error: {e}")
            raise
    
    async def add_sample_products(self):
        """Add sample products if database is empty"""
        try:
            # Products are already added via add_products.py script
            # This method is kept for reference but disabled to prevent threading issues
            pass
                
        except Exception as e:
            logger.error(f"Error adding sample products: {e}")
    
    async def on_ready(self):
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="the shop | /shop"
            )
        )
    
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return
        
        logger.error(f"Command error: {error}")
        
        embed = discord.Embed(
            title="❌ Error",
            description=f"An error occurred: {str(error)}",
            color=discord.Color.red()
        )
        
        try:
            await ctx.send(embed=embed, ephemeral=True)
        except:
            pass

# Initialize bot instance
bot = ShopBot()

if __name__ == "__main__":
    # This file should not be run directly
    # Use run.py instead
    pass
