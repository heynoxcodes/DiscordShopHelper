import discord
from datetime import datetime
from bot.config import Config

class EmbedBuilder:
    @staticmethod
    def success(title, description=None):
        embed = discord.Embed(
            title=f"✅ {title}",
            description=description,
            color=Config.SUCCESS_COLOR,
            timestamp=datetime.utcnow()
        )
        return embed
    
    @staticmethod
    def error(title, description=None):
        embed = discord.Embed(
            title=f"❌ {title}",
            description=description,
            color=Config.ERROR_COLOR,
            timestamp=datetime.utcnow()
        )
        return embed
    
    @staticmethod
    def warning(title, description=None):
        embed = discord.Embed(
            title=f"⚠️ {title}",
            description=description,
            color=Config.WARNING_COLOR,
            timestamp=datetime.utcnow()
        )
        return embed
    
    @staticmethod
    def info(title, description=None):
        embed = discord.Embed(
            title=title,
            description=description,
            color=Config.EMBED_COLOR,
            timestamp=datetime.utcnow()
        )
        return embed
    
    @staticmethod
    def product_catalog(products, category=None):
        title = f"🛍️ Shop - {category.title()}" if category else "🛍️ Product Catalog"
        embed = discord.Embed(
            title=title,
            color=Config.EMBED_COLOR,
            timestamp=datetime.utcnow()
        )
        
        if not products:
            embed.description = "No products available in this category."
            return embed
        
        for product in products[:10]:  # Limit to 10 products per embed
            stock_text = f"Stock: {product['stock']}" if product['stock'] > 0 else "❌ Out of Stock"
            embed.add_field(
                name=f"{product['name']} - ${product['price']:.2f}",
                value=f"{product['description']}\n{stock_text}",
                inline=True
            )
        
        if len(products) > 10:
            embed.set_footer(text=f"Showing 10 of {len(products)} products")
        
        return embed
    
    @staticmethod
    def order_confirmation(order):
        embed = discord.Embed(
            title="📋 Order Confirmation",
            color=Config.EMBED_COLOR,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Order ID", value=f"`{order['id']}`", inline=True)
        embed.add_field(name="Product", value=order['product_name'], inline=True)
        embed.add_field(name="Total", value=f"${order['total']:.2f}", inline=True)
        embed.add_field(name="Payment Method", value=order['payment_method'].title(), inline=True)
        embed.add_field(name="Status", value=order['status'].title(), inline=True)
        embed.add_field(name="Created", value=f"<t:{int(order['created_at'])}:R>", inline=True)
        
        if order['status'] == 'pending':
            embed.description = "⏳ Your order is pending payment. Please complete the payment to proceed."
        elif order['status'] == 'processing':
            embed.description = "🔄 Your order is being processed. You'll receive your items soon!"
        elif order['status'] == 'completed':
            embed.description = "✅ Your order has been completed! Thank you for your purchase."
        elif order['status'] == 'cancelled':
            embed.description = "❌ Your order has been cancelled."
        
        return embed
    
    @staticmethod
    def payment_instructions(order, payment_method):
        embed = discord.Embed(
            title="💳 Payment Instructions",
            color=Config.WARNING_COLOR,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Order ID", value=f"`{order['id']}`", inline=False)
        embed.add_field(name="Amount", value=f"${order['total']:.2f}", inline=False)
        
        if payment_method == 'paypal':
            embed.description = "Click the button below to pay with PayPal"
        elif payment_method == 'eth':
            embed.add_field(
                name="Ethereum Address",
                value=f"`{Config.ETH_WALLET_ADDRESS}`",
                inline=False
            )
            embed.description = "Send the exact amount to the address above"
        elif payment_method == 'ltc':
            embed.add_field(
                name="Litecoin Address", 
                value=f"`{Config.LTC_WALLET_ADDRESS}`",
                inline=False
            )
            embed.description = "Send the exact amount to the address above"
        elif payment_method == 'cashapp':
            embed.add_field(
                name="CashApp Tag",
                value=Config.CASHAPP_USERNAME,
                inline=False
            )
            embed.description = f"Send ${order['total']:.2f} to {Config.CASHAPP_USERNAME} with memo: {order['id']}"
        
        embed.set_footer(text="Payment must be completed within 30 minutes")
        return embed
