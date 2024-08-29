from pyrogram import Client
import re
import asyncio

from constants import (API_ID, API_HASH, SOLANA_WALLET_PATTERN,
                       TRON_WALLET_PATTERN, SYMBOL_PATTERN)


class TelegramClient:
    def __init__(self, api_id, api_hash, phone_number,
                 name='MainSession'):
        self.client = Client(name=name,
                             api_id=api_id,
                             api_hash=api_hash,
                             phone_number=phone_number)
        self.tron_coins = set()


    async def start(self):
        await self.client.start()

    async def stop(self):
        await self.client.stop()

    async def get_me(self):
        return await self.client.get_me()

    async def __get_last_messages(self, chat_id):
        messages = []
        try:
            async for message in self.client.get_chat_history(chat_id, limit=30):
                if message.caption:
                    messages.append(message.caption)
            return messages
        except Exception as e:
            return print(f"В TG возникла ошибка: {e}")

    async def parse_tron_coins(self, chat_id):
        messages = await self.__get_last_messages(chat_id)
        for message in messages:
            matches = re.findall(TRON_WALLET_PATTERN, message)
            self.tron_coins.update(matches)

    @self.client.on_message(filters.chat("POSEIDON_DEGEN_CALLS"))
    async def wait_new_message(self):