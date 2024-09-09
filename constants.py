import os
import re

import toml

script_dir = os.path.dirname(os.path.abspath(__file__))
toml_path = os.path.join(script_dir, 'data.toml')

if not os.path.exists(toml_path):
    raise FileNotFoundError(f"No such file or directory: '{toml_path}'")

with open(toml_path, 'r') as file:
    toml_content = file.read()


parsed_toml = toml.loads(toml_content)

API_ID = parsed_toml['TELEGRAM']['API_ID']
API_HASH = parsed_toml['TELEGRAM']['API_HASH']

PRIVATE_KEY = parsed_toml['TRON']['PRIVATE_KEY']
SEED_PHRASE = parsed_toml['TRON']['SEED_PHRASE']
HEX_TRX = parsed_toml['TRON']['HEX_TRX']
ROUTER_ADDRESS = parsed_toml['TRON']['ROUTER_ADDRESS']
BASE58_TRX = parsed_toml['TRON']['BASE58_TRX']
INFINITY_VALUE = 2**256 - 1

SYMBOL_PATTERN = re.compile(parsed_toml['REGEX']['SYMBOL_PATTERN'])
TRON_WALLET_PATTERN = re.compile(parsed_toml['REGEX']['TRON_WALLET_PATTERN'])
SOLANA_WALLET_PATTERN = re.compile(parsed_toml['REGEX']['SOLANA_WALLET_PATTERN'])