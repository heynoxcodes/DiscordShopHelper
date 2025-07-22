import discord
from discord.ext import commands
from bot.config import Config

def is_admin():
    """Check if user is an admin"""
    async def predicate(interaction: discord.Interaction):
        # Owner check
        if interaction.user.id == Config.OWNER_ID:
            return True
        
        # Admin role check
        if Config.ADMIN_ROLE_ID and interaction.guild and hasattr(interaction.user, 'roles'):
            admin_role = interaction.guild.get_role(Config.ADMIN_ROLE_ID)
            if admin_role and admin_role in interaction.user.roles:
                return True
        
        # Server permissions check
        if hasattr(interaction.user, 'guild_permissions') and interaction.user.guild_permissions.administrator:
            return True
        
        await interaction.response.send_message(
            "❌ You don't have permission to use this command.",
            ephemeral=True
        )
        return False
    
    return discord.app_commands.check(predicate)

def is_owner():
    """Check if user is the bot owner"""
    async def predicate(interaction: discord.Interaction):
        if interaction.user.id == Config.OWNER_ID:
            return True
        
        await interaction.response.send_message(
            "❌ Only the bot owner can use this command.",
            ephemeral=True
        )
        return False
    
    return discord.app_commands.check(predicate)
