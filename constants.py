import toml
import re

with open('data.toml', 'r') as file:
    toml_content = file.read()

parsed_toml = toml.loads(toml_content)

API_ID = parsed_toml['TELEGRAM']['API_ID']
API_HASH = parsed_toml['TELEGRAM']['API_HASH']
PRIVATE_KEY = parsed_toml['TELEGRAM']['PRIVATE_KEY']

SYMBOL_PATTERN = re.compile(parsed_toml['REGEX']['SYMBOL_PATTERN'])
TRON_WALLET_PATTERN = re.compile(parsed_toml['REGEX']['TRON_WALLET_PATTERN'])
SOLANA_WALLET_PATTERN = re.compile(parsed_toml['REGEX']['SOLANA_WALLET_PATTERN'])