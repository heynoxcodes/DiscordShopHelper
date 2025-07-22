import sqlite3
import asyncio
from datetime import datetime
import json

class DatabaseModels:
    """Database schema and models"""
    
    @staticmethod
    def get_schema():
        return {
            'products': '''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    category TEXT NOT NULL,
                    stock INTEGER DEFAULT 0,
                    image_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''',
            
            'orders': '''
                CREATE TABLE IF NOT EXISTS orders (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    product_name TEXT NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    unit_price REAL NOT NULL,
                    total REAL NOT NULL,
                    payment_method TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    payment_id TEXT,
                    delivery_info TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''',
            
            'payments': '''
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT NOT NULL,
                    payment_method TEXT NOT NULL,
                    payment_id TEXT,
                    amount REAL NOT NULL,
                    status TEXT DEFAULT 'pending',
                    transaction_hash TEXT,
                    webhook_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (order_id) REFERENCES orders (id)
                )
            ''',
            
            'inventory_logs': '''
                CREATE TABLE IF NOT EXISTS inventory_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    change_type TEXT NOT NULL,
                    quantity_change INTEGER NOT NULL,
                    old_stock INTEGER NOT NULL,
                    new_stock INTEGER NOT NULL,
                    reason TEXT,
                    admin_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''',
            
            'user_profiles': '''
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id INTEGER PRIMARY KEY,
                    total_spent REAL DEFAULT 0,
                    total_orders INTEGER DEFAULT 0,
                    first_purchase TIMESTAMP,
                    last_purchase TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            
            'support_tickets': '''
                CREATE TABLE IF NOT EXISTS support_tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    order_id TEXT,
                    subject TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'open',
                    priority TEXT DEFAULT 'medium',
                    assigned_to INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    closed_at TIMESTAMP,
                    FOREIGN KEY (order_id) REFERENCES orders (id)
                )
            ''',
            
            'settings': '''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''
        }
    
    @staticmethod
    def get_indexes():
        return [
            'CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)',
            'CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at)',
            'CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)',
            'CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active)',
            'CREATE INDEX IF NOT EXISTS idx_payments_order_id ON payments(order_id)',
            'CREATE INDEX IF NOT EXISTS idx_support_tickets_user_id ON support_tickets(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_support_tickets_status ON support_tickets(status)'
        ]
