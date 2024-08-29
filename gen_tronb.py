import tronpy
from tronpy.keys import PrivateKey

def tron_wallet_generator():
    while True:
        priv_key = PrivateKey.random()
        wallet_address = priv_key.public_key.to_base58check_address()
        yield wallet_address

# Example usage
wallet_gen = tron_wallet_generator()
for _ in range(10000):
    print(next(wallet_gen))