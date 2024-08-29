from pyrogram import Client, filters
from pyrogram.types import Message
import re

coin_pattern = r'\$\s*([A-Za-z]+)'
tron_wallet_pattern = r'T[1-9A-HJ-NP-Za-km-z]{33}'
solana_wallet_pattern = r'[1-9A-HJ-NP-Za-km-z]{32,44}'

coins = set()

bot = Client(name='MainSession',
             api_id=29131368,
             api_hash='4bc83f41154e6092e4fc2aaa3be82f97',
             phone_number='+79635763362')

async def main():
    async with bot:
        # "me" refers to your own chat (Saved Messages)
        async for message in bot.get_chat_history(chat_id="POSEIDON_DEGEN_CALLS", limit=20):
            matches = re.findall(solana_wallet_pattern, message.caption)
            print(matches)
            if any(keyword in message.caption for keyword in ['solana', 'Sol']):
                coins.update(matches)
                print(message.caption)
        print(coins)


bot.run(main())