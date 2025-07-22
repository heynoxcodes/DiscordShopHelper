import discord
from discord.ext import commands
from discord import app_commands
from bot.config import Config
from bot.utils.embeds import EmbedBuilder
from bot.utils.logger import setup_logger

logger = setup_logger()

class ShopCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="shop", description="Browse the product catalog")
    @app_commands.describe(category="Filter by category")
    @app_commands.choices(category=[
        app_commands.Choice(name="All", value="all"),
        app_commands.Choice(name="Robux", value="robux"),
        app_commands.Choice(name="Discord Nitro", value="nitro"),
        app_commands.Choice(name="Decorations", value="decorations")
    ])
    async def shop(self, interaction: discord.Interaction, category: str = "all"):
        """Display the shop catalog"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Get products from database
            if category == "all":
                products = await self.bot.db.get_products()
            else:
                products = await self.bot.db.get_products(category=category)
            
            embed = EmbedBuilder.product_catalog(products, category if category != "all" else None)
            
            if products:
                view = ShopView(self.bot, products)
                await interaction.followup.send(embed=embed, view=view)
            else:
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error in shop command: {e}")
            embed = EmbedBuilder.error("Shop Error", "Failed to load products. Please try again.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="buy", description="Purchase a product")
    @app_commands.describe(
        product_id="The ID of the product to purchase",
        quantity="Number of items to purchase"
    )
    async def buy(self, interaction: discord.Interaction, product_id: int, quantity: int = 1):
        """Purchase a product"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Validate inputs
            if quantity < 1 or quantity > 10:
                embed = EmbedBuilder.error("Invalid Quantity", "Quantity must be between 1 and 10.")
                await interaction.followup.send(embed=embed)
                return
            
            # Get product
            product = await self.bot.db.get_product(product_id)
            if not product:
                embed = EmbedBuilder.error("Product Not Found", "The specified product doesn't exist.")
                await interaction.followup.send(embed=embed)
                return
            
            if not product['is_active']:
                embed = EmbedBuilder.error("Product Unavailable", "This product is currently unavailable.")
                await interaction.followup.send(embed=embed)
                return
            
            if product['stock'] < quantity:
                embed = EmbedBuilder.error("Insufficient Stock", f"Only {product['stock']} items available.")
                await interaction.followup.send(embed=embed)
                return
            
            # Show purchase confirmation
            embed = discord.Embed(
                title="🛒 Purchase Confirmation",
                color=Config.EMBED_COLOR
            )
            embed.add_field(name="Product", value=product['name'], inline=True)
            embed.add_field(name="Quantity", value=str(quantity), inline=True)
            embed.add_field(name="Unit Price", value=f"${product['price']:.2f}", inline=True)
            embed.add_field(name="Total", value=f"${product['price'] * quantity:.2f}", inline=True)
            embed.set_footer(text="Choose your payment method below")
            
            view = PaymentMethodView(self.bot, product, quantity, interaction.user.id)
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Error in buy command: {e}")
            embed = EmbedBuilder.error("Purchase Error", "Failed to process purchase. Please try again.")
            await interaction.followup.send(embed=embed)

class ShopView(discord.ui.View):
    def __init__(self, bot, products):
        super().__init__(timeout=300)
        self.bot = bot
        self.products = products
        
        # Add category buttons
        for category_key, category_info in Config.CATEGORIES.items():
            button = discord.ui.Button(
                label=category_info['name'],
                emoji=category_info['emoji'],
                custom_id=f"category_{category_key}",
                style=discord.ButtonStyle.secondary
            )
            button.callback = self.category_callback
            self.add_item(button)
    
    async def category_callback(self, interaction: discord.Interaction):
        if not interaction.data or 'custom_id' not in interaction.data:
            return
        category = interaction.data['custom_id'].replace('category_', '')
        
        try:
            products = await self.bot.db.get_products(category=category)
            embed = EmbedBuilder.product_catalog(products, category)
            
            new_view = ShopView(self.bot, products)
            await interaction.response.edit_message(embed=embed, view=new_view)
            
        except Exception as e:
            logger.error(f"Error in category callback: {e}")
            await interaction.response.send_message("Failed to load category.", ephemeral=True)

class PaymentMethodView(discord.ui.View):
    def __init__(self, bot, product, quantity, user_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.product = product
        self.quantity = quantity
        self.user_id = user_id
        
        # Add payment method buttons
        for method_key, method_info in Config.PAYMENT_METHODS.items():
            if method_info['enabled']:
                button = discord.ui.Button(
                    label=method_info['name'],
                    emoji=method_info['emoji'],
                    custom_id=f"pay_{method_key}",
                    style=discord.ButtonStyle.primary
                )
                button.callback = self.payment_callback
                self.add_item(button)
    
    async def payment_callback(self, interaction: discord.Interaction):
        if not interaction.data or 'custom_id' not in interaction.data:
            return
        payment_method = interaction.data['custom_id'].replace('pay_', '')
        
        try:
            # Create order
            order_id = await self.bot.db.create_order(
                self.user_id,
                self.product['id'],
                self.quantity,
                payment_method
            )
            
            if not order_id:
                embed = EmbedBuilder.error("Order Failed", "Failed to create order. Product may be out of stock.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Get the created order
            order = await self.bot.db.get_order(order_id)
            
            # Show payment instructions
            embed = EmbedBuilder.payment_instructions(order, payment_method)
            
            if payment_method == 'paypal':
                view = PayPalPaymentView(self.bot, order)
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            else:
                view = CryptoPaymentView(self.bot, order)
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in payment callback: {e}")
            embed = EmbedBuilder.error("Payment Error", "Failed to process payment. Please try again.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

class PayPalPaymentView(discord.ui.View):
    def __init__(self, bot, order):
        super().__init__(timeout=1800)  # 30 minutes
        self.bot = bot
        self.order = order
    
    @discord.ui.button(label="Pay with PayPal", emoji="💰", style=discord.ButtonStyle.success)
    async def paypal_payment(self, interaction: discord.Interaction, button: discord.ui.Button):
        from bot.payments.paypal import PayPalHandler
        
        try:
            paypal = PayPalHandler()
            payment_url = await paypal.create_payment(self.order)
            
            if payment_url:
                embed = EmbedBuilder.info(
                    "PayPal Payment",
                    f"[Click here to complete your payment]({payment_url})\n\n"
                    f"Order ID: `{self.order['id']}`\n"
                    f"Amount: ${self.order['total']:.2f}"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = EmbedBuilder.error("Payment Error", "Failed to create PayPal payment.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
        except Exception as e:
            logger.error(f"PayPal payment error: {e}")
            embed = EmbedBuilder.error("Payment Error", "Failed to process PayPal payment.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

class CryptoPaymentView(discord.ui.View):
    def __init__(self, bot, order):
        super().__init__(timeout=1800)  # 30 minutes
        self.bot = bot
        self.order = order
    
    @discord.ui.button(label="I've Sent Payment", emoji="✅", style=discord.ButtonStyle.success)
    async def payment_sent(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = EmbedBuilder.success(
            "Payment Confirmation Received",
            f"We've received your payment confirmation for order `{self.order['id']}`.\n"
            "Our team will verify the transaction and process your order within 10-30 minutes.\n\n"
            "You'll receive a notification once your order is completed."
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Update order status to processing
        await self.bot.db.update_order_status(self.order['id'], 'processing')
    
    @discord.ui.button(label="Cancel Order", emoji="❌", style=discord.ButtonStyle.danger)
    async def cancel_order(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.bot.db.update_order_status(self.order['id'], 'cancelled')
        
        embed = EmbedBuilder.warning(
            "Order Cancelled",
            f"Order `{self.order['id']}` has been cancelled."
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ShopCommands(bot))
