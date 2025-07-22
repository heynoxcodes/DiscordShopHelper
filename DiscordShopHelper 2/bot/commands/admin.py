import discord
from discord.ext import commands
from discord import app_commands
from bot.utils.embeds import EmbedBuilder
from bot.utils.permissions import is_admin, is_owner
from bot.utils.logger import setup_logger
from bot.config import Config

logger = setup_logger()

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="admin", description="Admin dashboard")
    @is_admin()
    async def admin_dashboard(self, interaction: discord.Interaction):
        """Show admin dashboard"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Get analytics
            analytics = await self.bot.db.get_sales_analytics(days=7)
            
            embed = discord.Embed(
                title="🛠️ Admin Dashboard",
                color=Config.EMBED_COLOR
            )
            
            embed.add_field(
                name="📊 Last 7 Days",
                value=(
                    f"**Orders:** {analytics['total_orders']}\n"
                    f"**Revenue:** ${analytics['total_revenue']:.2f}"
                ),
                inline=True
            )
            
            # Pending orders
            async with await self.bot.db.get_connection() as db:
                async with db.execute(
                    "SELECT COUNT(*) FROM orders WHERE status = 'pending'"
                ) as cursor:
                    pending_orders = (await cursor.fetchone())[0]
                
                async with db.execute(
                    "SELECT COUNT(*) FROM orders WHERE status = 'processing'"
                ) as cursor:
                    processing_orders = (await cursor.fetchone())[0]
            
            embed.add_field(
                name="⏳ Order Status",
                value=(
                    f"**Pending:** {pending_orders}\n"
                    f"**Processing:** {processing_orders}"
                ),
                inline=True
            )
            
            # Low stock products
            async with await self.bot.db.get_connection() as db:
                async with db.execute(
                    "SELECT name, stock FROM products WHERE stock < 5 AND is_active = 1"
                ) as cursor:
                    low_stock = await cursor.fetchall()
            
            if low_stock:
                low_stock_text = "\n".join([f"• {name}: {stock}" for name, stock in low_stock[:5]])
                embed.add_field(
                    name="⚠️ Low Stock",
                    value=low_stock_text,
                    inline=False
                )
            
            view = AdminDashboardView(self.bot)
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Error in admin dashboard: {e}")
            embed = EmbedBuilder.error("Dashboard Error", "Failed to load admin dashboard.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="add_product", description="Add a new product")
    @is_admin()
    async def add_product(self, interaction: discord.Interaction):
        """Add a new product"""
        modal = AddProductModal(self.bot)
        await interaction.response.send_modal(modal)
    
    @app_commands.command(name="update_stock", description="Update product stock")
    @app_commands.describe(
        product_id="The ID of the product",
        stock="New stock amount",
        reason="Reason for stock update"
    )
    @is_admin()
    async def update_stock(self, interaction: discord.Interaction, product_id: int, stock: int, reason: str = "Admin update"):
        """Update product stock"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            success = await self.bot.db.update_product_stock(
                product_id, stock, interaction.user.id, reason
            )
            
            if success:
                embed = EmbedBuilder.success(
                    "Stock Updated",
                    f"Product ID {product_id} stock updated to {stock}"
                )
            else:
                embed = EmbedBuilder.error("Update Failed", "Product not found.")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error updating stock: {e}")
            embed = EmbedBuilder.error("Stock Update Error", "Failed to update stock.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="manage_order", description="Manage an order")
    @app_commands.describe(
        order_id="The order ID to manage",
        status="New order status"
    )
    @app_commands.choices(status=[
        app_commands.Choice(name="Pending", value="pending"),
        app_commands.Choice(name="Processing", value="processing"), 
        app_commands.Choice(name="Completed", value="completed"),
        app_commands.Choice(name="Cancelled", value="cancelled")
    ])
    @is_admin()
    async def manage_order(self, interaction: discord.Interaction, order_id: str, status: str):
        """Manage order status"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            order = await self.bot.db.get_order(order_id.upper())
            if not order:
                embed = EmbedBuilder.error("Order Not Found", f"Order `{order_id}` was not found.")
                await interaction.followup.send(embed=embed)
                return
            
            # Update order status
            await self.bot.db.update_order_status(order_id.upper(), status)
            
            # If completing order, update user profile and reduce stock
            if status == 'completed' and order['status'] != 'completed':
                await self.bot.db.update_user_profile(order['user_id'], order['total'])
                
                # Reduce stock
                product = await self.bot.db.get_product(order['product_id'])
                if product:
                    new_stock = max(0, product['stock'] - order['quantity'])
                    await self.bot.db.update_product_stock(
                        order['product_id'], new_stock, interaction.user.id, f"Order {order_id} completed"
                    )
            
            embed = EmbedBuilder.success(
                "Order Updated",
                f"Order `{order_id}` status changed to **{status}**"
            )
            
            await interaction.followup.send(embed=embed)
            
            # Notify customer
            try:
                user = self.bot.get_user(order['user_id'])
                if user:
                    customer_embed = EmbedBuilder.order_confirmation(order)
                    customer_embed.title = f"📋 Order {order_id} Updated"
                    await user.send(embed=customer_embed)
            except:
                pass  # User might have DMs disabled
            
        except Exception as e:
            logger.error(f"Error managing order: {e}")
            embed = EmbedBuilder.error("Order Management Error", "Failed to update order.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="sales_report", description="Generate sales report")
    @app_commands.describe(days="Number of days to include in report")
    @is_admin()
    async def sales_report(self, interaction: discord.Interaction, days: int = 30):
        """Generate sales report"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            analytics = await self.bot.db.get_sales_analytics(days)
            
            embed = discord.Embed(
                title=f"📊 Sales Report - Last {days} Days",
                color=Config.EMBED_COLOR
            )
            
            embed.add_field(
                name="📈 Overview",
                value=(
                    f"**Total Orders:** {analytics['total_orders']}\n"
                    f"**Total Revenue:** ${analytics['total_revenue']:.2f}\n"
                    f"**Average Order:** ${analytics['total_revenue']/max(analytics['total_orders'], 1):.2f}"
                ),
                inline=False
            )
            
            # Category breakdown
            if analytics['category_sales']:
                category_text = "\n".join([
                    f"**{cat}:** {count} orders (${revenue:.2f})"
                    for cat, count, revenue in analytics['category_sales']
                ])
                embed.add_field(
                    name="📦 By Category",
                    value=category_text,
                    inline=False
                )
            
            # Top products
            if analytics['top_products']:
                product_text = "\n".join([
                    f"**{name}:** {count} sales (${revenue:.2f})"
                    for name, count, revenue in analytics['top_products']
                ])
                embed.add_field(
                    name="🏆 Top Products",
                    value=product_text,
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error generating sales report: {e}")
            embed = EmbedBuilder.error("Report Error", "Failed to generate sales report.")
            await interaction.followup.send(embed=embed)

class AdminDashboardView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
    
    @discord.ui.button(label="Pending Orders", emoji="⏳", style=discord.ButtonStyle.secondary)
    async def pending_orders(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        try:
            async with await self.bot.db.get_connection() as db:
                async with db.execute(
                    '''SELECT o.*, u.name as username FROM orders o
                       LEFT JOIN user_profiles u ON o.user_id = u.user_id
                       WHERE o.status = 'pending'
                       ORDER BY o.created_at DESC
                       LIMIT 10'''
                ) as cursor:
                    orders = await cursor.fetchall()
            
            if not orders:
                embed = EmbedBuilder.info("No Pending Orders", "All orders are up to date!")
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="⏳ Pending Orders",
                color=Config.WARNING_COLOR
            )
            
            for order in orders:
                embed.add_field(
                    name=f"Order {order[0]}",
                    value=(
                        f"**User:** <@{order[1]}>\n"
                        f"**Product:** {order[3]}\n"
                        f"**Total:** ${order[6]:.2f}\n"
                        f"**Payment:** {order[7].title()}"
                    ),
                    inline=True
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error loading pending orders: {e}")
            embed = EmbedBuilder.error("Load Error", "Failed to load pending orders.")
            await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="Low Stock", emoji="⚠️", style=discord.ButtonStyle.danger)
    async def low_stock(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        try:
            products = await self.bot.db.get_products()
            low_stock_products = [p for p in products if p['stock'] < 5 and p['is_active']]
            
            if not low_stock_products:
                embed = EmbedBuilder.success("Stock Levels Good", "All products have adequate stock!")
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="⚠️ Low Stock Alert",
                color=Config.WARNING_COLOR
            )
            
            for product in low_stock_products[:10]:
                embed.add_field(
                    name=f"{product['name']} (ID: {product['id']})",
                    value=f"Stock: {product['stock']}\nPrice: ${product['price']:.2f}",
                    inline=True
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error loading low stock: {e}")
            embed = EmbedBuilder.error("Load Error", "Failed to load stock information.")
            await interaction.followup.send(embed=embed)

class AddProductModal(discord.ui.Modal):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(title="Add New Product")
        
        self.name = discord.ui.TextInput(
            label="Product Name",
            placeholder="Enter product name...",
            required=True,
            max_length=100
        )
        
        self.description = discord.ui.TextInput(
            label="Description",
            placeholder="Enter product description...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500
        )
        
        self.price = discord.ui.TextInput(
            label="Price (USD)",
            placeholder="0.00",
            required=True,
            max_length=10
        )
        
        self.category = discord.ui.TextInput(
            label="Category",
            placeholder="robux, nitro, decorations",
            required=True,
            max_length=50
        )
        
        self.stock = discord.ui.TextInput(
            label="Initial Stock",
            placeholder="0",
            required=True,
            max_length=10
        )
        
        self.add_item(self.name)
        self.add_item(self.description)
        self.add_item(self.price)
        self.add_item(self.category)
        self.add_item(self.stock)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Validate inputs
            try:
                price = float(self.price.value)
                stock = int(self.stock.value)
            except ValueError:
                embed = EmbedBuilder.error("Invalid Input", "Price must be a number and stock must be an integer.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if price < 0 or stock < 0:
                embed = EmbedBuilder.error("Invalid Input", "Price and stock must be positive numbers.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if self.category.value.lower() not in Config.CATEGORIES:
                embed = EmbedBuilder.error(
                    "Invalid Category", 
                    f"Category must be one of: {', '.join(Config.CATEGORIES.keys())}"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Create product
            product_id = await self.bot.db.create_product(
                self.name.value,
                self.description.value,
                price,
                self.category.value.lower(),
                stock
            )
            
            embed = EmbedBuilder.success(
                "Product Added",
                f"Product '{self.name.value}' has been added successfully!\n"
                f"**ID:** {product_id}\n"
                f"**Price:** ${price:.2f}\n"
                f"**Stock:** {stock}"
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error adding product: {e}")
            embed = EmbedBuilder.error("Product Creation Error", "Failed to add product. Please try again.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
