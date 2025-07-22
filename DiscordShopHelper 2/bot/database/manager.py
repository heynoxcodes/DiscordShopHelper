import sqlite3
import asyncio
import aiosqlite
import json
from datetime import datetime
import uuid
from bot.config import Config
from bot.database.models import DatabaseModels
from bot.utils.logger import setup_logger

logger = setup_logger()

class DatabaseManager:
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        self._connection_pool = None
    
    async def initialize(self):
        """Initialize database and create tables"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Create tables
                schema = DatabaseModels.get_schema()
                for table_name, create_sql in schema.items():
                    await db.execute(create_sql)
                    logger.info(f"Created/verified table: {table_name}")
                
                # Create indexes
                indexes = DatabaseModels.get_indexes()
                for index_sql in indexes:
                    await db.execute(index_sql)
                
                await db.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def get_connection(self):
        """Get database connection"""
        return await aiosqlite.connect(self.db_path)
    
    # Product methods
    async def create_product(self, name, description, price, category, stock=0, image_url=None):
        """Create a new product"""
        async with await self.get_connection() as db:
            cursor = await db.execute(
                '''INSERT INTO products (name, description, price, category, stock, image_url)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (name, description, price, category, stock, image_url)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def get_products(self, category=None, active_only=True):
        """Get products, optionally filtered by category"""
        async with await self.get_connection() as db:
            if category:
                sql = 'SELECT * FROM products WHERE category = ?'
                params = [category]
            else:
                sql = 'SELECT * FROM products WHERE 1=1'
                params = []
            
            if active_only:
                sql += ' AND is_active = 1'
            
            sql += ' ORDER BY created_at DESC'
            
            async with db.execute(sql, params) as cursor:
                rows = await cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
    
    async def get_product(self, product_id):
        """Get a single product by ID"""
        async with await self.get_connection() as db:
            async with db.execute('SELECT * FROM products WHERE id = ?', (product_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None
    
    async def update_product_stock(self, product_id, new_stock, admin_id=None, reason=None):
        """Update product stock and log the change"""
        async with await self.get_connection() as db:
            # Get current stock
            async with db.execute('SELECT stock FROM products WHERE id = ?', (product_id,)) as cursor:
                result = await cursor.fetchone()
                if not result:
                    return False
                
                old_stock = result[0]
            
            # Update stock
            await db.execute(
                'UPDATE products SET stock = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (new_stock, product_id)
            )
            
            # Log the change
            change_type = 'increase' if new_stock > old_stock else 'decrease'
            quantity_change = new_stock - old_stock
            
            await db.execute(
                '''INSERT INTO inventory_logs 
                   (product_id, change_type, quantity_change, old_stock, new_stock, reason, admin_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (product_id, change_type, quantity_change, old_stock, new_stock, reason, admin_id)
            )
            
            await db.commit()
            return True
    
    # Order methods
    async def create_order(self, user_id, product_id, quantity, payment_method):
        """Create a new order"""
        async with await self.get_connection() as db:
            # Get product info
            product = await self.get_product(product_id)
            if not product or product['stock'] < quantity:
                return None
            
            order_id = str(uuid.uuid4())[:8].upper()
            total = product['price'] * quantity
            
            await db.execute(
                '''INSERT INTO orders 
                   (id, user_id, product_id, product_name, quantity, unit_price, total, payment_method)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (order_id, user_id, product_id, product['name'], quantity, product['price'], total, payment_method)
            )
            
            await db.commit()
            return order_id
    
    async def get_order(self, order_id):
        """Get order by ID"""
        async with await self.get_connection() as db:
            async with db.execute('SELECT * FROM orders WHERE id = ?', (order_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None
    
    async def get_user_orders(self, user_id, limit=10):
        """Get user's orders"""
        async with await self.get_connection() as db:
            async with db.execute(
                'SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT ?',
                (user_id, limit)
            ) as cursor:
                rows = await cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
    
    async def update_order_status(self, order_id, status, payment_id=None):
        """Update order status"""
        async with await self.get_connection() as db:
            params = [status, order_id]
            sql = 'UPDATE orders SET status = ?, updated_at = CURRENT_TIMESTAMP'
            
            if payment_id:
                sql += ', payment_id = ?'
                params.insert(-1, payment_id)
            
            if status == 'completed':
                sql += ', completed_at = CURRENT_TIMESTAMP'
            
            sql += ' WHERE id = ?'
            
            await db.execute(sql, params)
            await db.commit()
    
    # User profile methods
    async def update_user_profile(self, user_id, order_total):
        """Update user profile after purchase"""
        async with await self.get_connection() as db:
            # Check if profile exists
            async with db.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,)) as cursor:
                profile = await cursor.fetchone()
            
            if profile:
                await db.execute(
                    '''UPDATE user_profiles 
                       SET total_spent = total_spent + ?, 
                           total_orders = total_orders + 1,
                           last_purchase = CURRENT_TIMESTAMP
                       WHERE user_id = ?''',
                    (order_total, user_id)
                )
            else:
                await db.execute(
                    '''INSERT INTO user_profiles 
                       (user_id, total_spent, total_orders, first_purchase, last_purchase)
                       VALUES (?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)''',
                    (user_id, order_total)
                )
            
            await db.commit()
    
    async def get_user_profile(self, user_id):
        """Get user profile"""
        async with await self.get_connection() as db:
            async with db.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None
    
    # Analytics methods
    async def get_sales_analytics(self, days=30):
        """Get sales analytics for the last N days"""
        async with await self.get_connection() as db:
            # Total sales
            async with db.execute(
                '''SELECT COUNT(*), SUM(total) FROM orders 
                   WHERE status = 'completed' AND created_at >= datetime('now', '-{} days')'''.format(days)
            ) as cursor:
                result = await cursor.fetchone()
                total_orders, total_revenue = result if result else (0, 0)
            
            # Sales by category
            async with db.execute(
                '''SELECT p.category, COUNT(o.id), SUM(o.total)
                   FROM orders o
                   JOIN products p ON o.product_id = p.id
                   WHERE o.status = 'completed' AND o.created_at >= datetime('now', '-{} days')
                   GROUP BY p.category'''.format(days)
            ) as cursor:
                category_sales = await cursor.fetchall()
            
            # Top products
            async with db.execute(
                '''SELECT product_name, COUNT(*), SUM(total)
                   FROM orders
                   WHERE status = 'completed' AND created_at >= datetime('now', '-{} days')
                   GROUP BY product_name
                   ORDER BY COUNT(*) DESC
                   LIMIT 5'''.format(days)
            ) as cursor:
                top_products = await cursor.fetchall()
            
            return {
                'total_orders': total_orders or 0,
                'total_revenue': total_revenue or 0,
                'category_sales': category_sales,
                'top_products': top_products
            }
