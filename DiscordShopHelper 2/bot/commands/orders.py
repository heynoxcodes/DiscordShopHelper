import discord
from discord.ext import commands
from discord import app_commands
from bot.utils.embeds import EmbedBuilder
from bot.utils.logger import setup_logger

logger = setup_logger()

class OrderCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="orders", description="View your order history")
    async def orders(self, interaction: discord.Interaction):
        """View user's order history"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            orders = await self.bot.db.get_user_orders(interaction.user.id, limit=10)
            
            if not orders:
                embed = EmbedBuilder.info(
                    "No Orders Found",
                    "You haven't made any purchases yet. Use `/shop` to browse products!"
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="📋 Your Order History",
                color=0x5865F2,
                description=f"Showing your last {len(orders)} orders"
            )
            
            for order in orders:
                status_emoji = {
                    'pending': '⏳',
                    'processing': '🔄',
                    'completed': '✅',
                    'cancelled': '❌'
                }.get(order['status'], '❓')
                
                embed.add_field(
                    name=f"{status_emoji} Order {order['id']}",
                    value=(
                        f"**Product:** {order['product_name']}\n"
                        f"**Total:** ${order['total']:.2f}\n"
                        f"**Status:** {order['status'].title()}\n"
                        f"**Date:** <t:{int(order['created_at'])}:R>"
                    ),
                    inline=True
                )
            
            # Add user stats
            profile = await self.bot.db.get_user_profile(interaction.user.id)
            if profile:
                embed.set_footer(
                    text=f"Total spent: ${profile['total_spent']:.2f} • Total orders: {profile['total_orders']}"
                )
            
            view = OrderHistoryView(self.bot, orders)
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Error in orders command: {e}")
            embed = EmbedBuilder.error("Orders Error", "Failed to load your orders. Please try again.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="order", description="View details of a specific order")
    @app_commands.describe(order_id="The ID of the order to view")
    async def order(self, interaction: discord.Interaction, order_id: str):
        """View specific order details"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            order = await self.bot.db.get_order(order_id.upper())
            
            if not order:
                embed = EmbedBuilder.error("Order Not Found", f"Order `{order_id}` was not found.")
                await interaction.followup.send(embed=embed)
                return
            
            # Check if user owns this order
            if order['user_id'] != interaction.user.id:
                embed = EmbedBuilder.error("Access Denied", "You can only view your own orders.")
                await interaction.followup.send(embed=embed)
                return
            
            embed = EmbedBuilder.order_confirmation(order)
            
            # Add additional details
            if order['delivery_info']:
                embed.add_field(name="Delivery Info", value=order['delivery_info'], inline=False)
            
            view = OrderDetailsView(self.bot, order)
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Error in order command: {e}")
            embed = EmbedBuilder.error("Order Error", "Failed to load order details. Please try again.")
            await interaction.followup.send(embed=embed)

class OrderHistoryView(discord.ui.View):
    def __init__(self, bot, orders):
        super().__init__(timeout=300)
        self.bot = bot
        self.orders = orders
        
        # Add dropdown for order selection
        self.add_item(OrderSelect(bot, orders))

class OrderSelect(discord.ui.Select):
    def __init__(self, bot, orders):
        self.bot = bot
        
        options = []
        for order in orders[:10]:  # Discord limit of 25 options
            status_emoji = {
                'pending': '⏳',
                'processing': '🔄', 
                'completed': '✅',
                'cancelled': '❌'
            }.get(order['status'], '❓')
            
            options.append(discord.SelectOption(
                label=f"Order {order['id']}",
                description=f"{order['product_name']} - ${order['total']:.2f}",
                emoji=status_emoji,
                value=order['id']
            ))
        
        super().__init__(
            placeholder="Select an order to view details...",
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        order_id = self.values[0]
        order = await self.bot.db.get_order(order_id)
        
        if order:
            embed = EmbedBuilder.order_confirmation(order)
            view = OrderDetailsView(self.bot, order)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        else:
            embed = EmbedBuilder.error("Order Not Found", "Failed to load order details.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

class OrderDetailsView(discord.ui.View):
    def __init__(self, bot, order):
        super().__init__(timeout=300)
        self.bot = bot
        self.order = order
        
        # Add support ticket button for pending/processing orders
        if order['status'] in ['pending', 'processing']:
            self.add_item(SupportTicketButton(bot, order))

class SupportTicketButton(discord.ui.Button):
    def __init__(self, bot, order):
        self.bot = bot
        self.order = order
        super().__init__(
            label="Need Help?",
            emoji="🎫",
            style=discord.ButtonStyle.secondary
        )
    
    async def callback(self, interaction: discord.Interaction):
        modal = SupportTicketModal(self.bot, self.order)
        await interaction.response.send_modal(modal)

class SupportTicketModal(discord.ui.Modal):
    def __init__(self, bot, order):
        self.bot = bot
        self.order = order
        super().__init__(title=f"Support Ticket - Order {order['id']}")
        
        self.subject = discord.ui.TextInput(
            label="Subject",
            placeholder="Brief description of your issue...",
            required=True,
            max_length=100
        )
        
        self.description = discord.ui.TextInput(
            label="Description", 
            placeholder="Please describe your issue in detail...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000
        )
        
        self.add_item(self.subject)
        self.add_item(self.description)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Create support ticket in database
            async with await self.bot.db.get_connection() as db:
                await db.execute(
                    '''INSERT INTO support_tickets (user_id, order_id, subject, description)
                       VALUES (?, ?, ?, ?)''',
                    (interaction.user.id, self.order['id'], self.subject.value, self.description.value)
                )
                await db.commit()
            
            embed = EmbedBuilder.success(
                "Support Ticket Created",
                f"Your support ticket has been created successfully.\n\n"
                f"**Subject:** {self.subject.value}\n"
                f"**Order:** {self.order['id']}\n\n"
                f"Our support team will respond to you soon."
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Notify admins (you can implement this based on your needs)
            # This could send a message to an admin channel
            
        except Exception as e:
            logger.error(f"Error creating support ticket: {e}")
            embed = EmbedBuilder.error("Ticket Error", "Failed to create support ticket. Please try again.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(OrderCommands(bot))
