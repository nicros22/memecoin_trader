import logging
import asyncio
from pyrogram import Client, filters
from telegram.client import TelegramClient
from constants import (API_ID, API_HASH, SOLANA_WALLET_PATTERN,
                       TRON_WALLET_PATTERN, SYMBOL_PATTERN)

async def main():
    tg_client = TelegramClient(api_hash=API_HASH,
                               api_id=API_ID,
                               phone_number='+79635763362')
    await tg_client.start()
    tg_client.add_message_handler("POSEIDON_DEGEN_CALLS")
    await asyncio.Event().wait()
    await tg_client.parse_tron_coins("POSEIDON_DEGEN_CALLS")
    print(tg_client.tron_coins)
    await tg_client.stop()


if __name__ == "__main__":
    asyncio.run(main())
