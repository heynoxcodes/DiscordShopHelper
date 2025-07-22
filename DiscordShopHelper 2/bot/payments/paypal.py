import aiohttp
import json
import base64
from urllib.parse import urljoin
from bot.config import Config
from bot.utils.logger import setup_logger

logger = setup_logger()

class PayPalHandler:
    def __init__(self):
        self.client_id = Config.PAYPAL_CLIENT_ID
        self.client_secret = Config.PAYPAL_CLIENT_SECRET
        self.is_sandbox = Config.PAYPAL_SANDBOX
        
        if self.is_sandbox:
            self.base_url = "https://api.sandbox.paypal.com"
            self.web_url = "https://www.sandbox.paypal.com"
        else:
            self.base_url = "https://api.paypal.com"
            self.web_url = "https://www.paypal.com"
        
        self.access_token = None
    
    async def get_access_token(self):
        """Get PayPal access token"""
        if not self.client_id or not self.client_secret:
            logger.error("PayPal credentials not configured")
            return None
        
        try:
            auth_string = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
            
            headers = {
                'Accept': 'application/json',
                'Accept-Language': 'en_US',
                'Authorization': f'Basic {auth_string}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = 'grant_type=client_credentials'
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/v1/oauth2/token",
                    headers=headers,
                    data=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.access_token = result.get('access_token')
                        return self.access_token
                    else:
                        logger.error(f"PayPal auth failed: {response.status}")
                        return None
        
        except Exception as e:
            logger.error(f"PayPal auth error: {e}")
            return None
    
    async def create_payment(self, order):
        """Create PayPal payment"""
        try:
            if not self.access_token:
                await self.get_access_token()
            
            if not self.access_token:
                return None
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.access_token}'
            }
            
            payment_data = {
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "transactions": [{
                    "amount": {
                        "total": f"{order['total']:.2f}",
                        "currency": "USD"
                    },
                    "description": f"Shop Order #{order['id']} - {order['product_name']}",
                    "custom": order['id']  # Store order ID for reference
                }],
                "redirect_urls": {
                    "return_url": "https://example.com/payment/success",  # You should replace this
                    "cancel_url": "https://example.com/payment/cancel"    # You should replace this
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/v1/payments/payment",
                    headers=headers,
                    json=payment_data
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        
                        # Find approval URL
                        for link in result.get('links', []):
                            if link.get('rel') == 'approval_url':
                                return link.get('href')
                        
                        logger.error("PayPal approval URL not found")
                        return None
                    else:
                        error_text = await response.text()
                        logger.error(f"PayPal payment creation failed: {response.status} - {error_text}")
                        return None
        
        except Exception as e:
            logger.error(f"PayPal payment creation error: {e}")
            return None
    
    async def execute_payment(self, payment_id, payer_id):
        """Execute PayPal payment after approval"""
        try:
            if not self.access_token:
                await self.get_access_token()
            
            if not self.access_token:
                return False
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.access_token}'
            }
            
            execute_data = {
                "payer_id": payer_id
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/v1/payments/payment/{payment_id}/execute",
                    headers=headers,
                    json=execute_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('state') == 'approved'
                    else:
                        error_text = await response.text()
                        logger.error(f"PayPal payment execution failed: {response.status} - {error_text}")
                        return False
        
        except Exception as e:
            logger.error(f"PayPal payment execution error: {e}")
            return False
    
    async def verify_payment(self, payment_id):
        """Verify PayPal payment status"""
        try:
            if not self.access_token:
                await self.get_access_token()
            
            if not self.access_token:
                return None
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.access_token}'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/v1/payments/payment/{payment_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        logger.error(f"PayPal payment verification failed: {response.status}")
                        return None
        
        except Exception as e:
            logger.error(f"PayPal payment verification error: {e}")
            return None
