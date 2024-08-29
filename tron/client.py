from tronpy import Tron
from tronpy.keys import PrivateKey

from constants import PRIVATE_KEY


class TronClient:
    def __init__(self, private_key: str, wallet: str, client):
        self.private_key = private_key
        self.wallet = wallet
        self.client = Tron()
# Initialize Tron connection


# Your private key (NEVER expose your private key)
private_key = "YOUR_PRIVATE_KEY_HERE"
wallet = PrivateKey(bytes.fromhex(private_key))

# TRC20 contract address (e.g., USDT on Tron)
contract_address = "CONTRACT_ADDRESS_OF_TRC20_TOKEN"

# Address to receive the tokens
to_address = "RECIPIENT_ADDRESS"