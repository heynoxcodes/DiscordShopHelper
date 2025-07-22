import aiohttp
import asyncio
from bot.config import Config
from bot.utils.logger import setup_logger

logger = setup_logger()

class CryptoHandler:
    def __init__(self):
        self.eth_address = Config.ETH_WALLET_ADDRESS
        self.ltc_address = Config.LTC_WALLET_ADDRESS
    
    async def get_eth_price(self):
        """Get current ETH price in USD"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['ethereum']['usd']
                    return None
        except Exception as e:
            logger.error(f"Error fetching ETH price: {e}")
            return None
    
    async def get_ltc_price(self):
        """Get current LTC price in USD"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.coingecko.com/api/v3/simple/price?ids=litecoin&vs_currencies=usd"
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['litecoin']['usd']
                    return None
        except Exception as e:
            logger.error(f"Error fetching LTC price: {e}")
            return None
    
    async def calculate_crypto_amount(self, usd_amount, crypto_type):
        """Calculate crypto amount needed for USD amount"""
        try:
            if crypto_type.lower() == 'eth':
                price = await self.get_eth_price()
            elif crypto_type.lower() == 'ltc':
                price = await self.get_ltc_price()
            else:
                return None
            
            if price:
                return usd_amount / price
            return None
        except Exception as e:
            logger.error(f"Error calculating crypto amount: {e}")
            return None
    
    async def verify_eth_transaction(self, tx_hash, expected_amount, to_address):
        """Verify Ethereum transaction (requires API key for full verification)"""
        try:
            # This is a basic implementation
            # For production, you'd want to use services like Etherscan API
            # or run your own Ethereum node
            
            api_key = "YourEtherscanAPIKey"  # You should get this from environment
            url = f"https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash={tx_hash}&apikey={api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = data.get('result')
                        
                        if result:
                            # Verify transaction details
                            to = result.get('to', '').lower()
                            value_wei = int(result.get('value', '0'), 16)
                            value_eth = value_wei / 10**18
                            
                            if to == to_address.lower() and abs(value_eth - expected_amount) < 0.001:
                                return True
                        
                        return False
                    return False
        except Exception as e:
            logger.error(f"Error verifying ETH transaction: {e}")
            return False
    
    async def verify_ltc_transaction(self, tx_hash, expected_amount, to_address):
        """Verify Litecoin transaction"""
        try:
            # This is a basic implementation
            # For production, you'd want to use services like BlockCypher API
            # or run your own Litecoin node
            
            url = f"https://api.blockcypher.com/v1/ltc/main/txs/{tx_hash}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check outputs for our address
                        outputs = data.get('outputs', [])
                        for output in outputs:
                            addresses = output.get('addresses', [])
                            value_satoshi = output.get('value', 0)
                            value_ltc = value_satoshi / 10**8
                            
                            if to_address in addresses and abs(value_ltc - expected_amount) < 0.001:
                                return True
                        
                        return False
                    return False
        except Exception as e:
            logger.error(f"Error verifying LTC transaction: {e}")
            return False
    
    async def monitor_address(self, address, crypto_type, expected_amount):
        """Monitor address for incoming transactions"""
        # This would be used to automatically detect payments
        # For now, it's a placeholder for manual verification
        pass
