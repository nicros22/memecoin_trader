import asyncio
import re

from constants import (API_HASH, API_ID, SOLANA_WALLET_PATTERN, SYMBOL_PATTERN,
                       TRON_WALLET_PATTERN)
from loguru import logger
from pyrogram import Client


class TelegramClient:
    def __init__(self, api_id, api_hash, phone_number, chat_id, name='MainSession'):
        logger.info("Инициализация TelegramClient")
        self.client = Client(name=name,
                             api_id=api_id,
                             api_hash=api_hash,
                             phone_number=phone_number)
        self.chat_id = chat_id
        self.tron_coins = set()
        self.solana_coins = set()
        self.message_received_event = asyncio.Event()
        self.coin_type = None
        self.new_coin = None

    async def start(self):
        logger.info("Запуск Telegram клиента")
        await self.client.start()

    async def stop(self):
        logger.info("Остановка Telegram клиента")
        await self.client.stop()

    async def get_me(self):
        logger.info("Получение информации о Telegram клиенте")
        return await self.client.get_me()

    async def __get_last_messages(self, chat_id, limit=30):
        logger.info(f"Получение последних {limit} сообщений из чата {chat_id}")
        messages = []
        try:
            async for message in self.client.get_chat_history(chat_id, limit=limit):
                caption = message.caption if message.caption else ""
                text = message.text if message.text else ""
                if 'Update' in caption or 'Update' in text:
                    continue
                messages.append(caption + text)
            return messages
        except Exception as e:
            logger.error(f"Ошибка при получении сообщений: {e}")
            return messages

    async def parse_coins(self, messages, tron=True, solana=True):
        logger.info("Парсинг монет из сообщений")
        tron_results = []
        solana_results = []
        for message in messages:
            if tron:
                match = re.search(TRON_WALLET_PATTERN, message)
                if match:
                    first_tron_coin = match.group()
                    if first_tron_coin not in self.tron_coins:
                        self.tron_coins.add(first_tron_coin)
                        tron_results.append(first_tron_coin)

            if solana:
                if any(keyword in message for keyword in ['solana', 'Sol']):
                    match = re.search(SOLANA_WALLET_PATTERN, message)
                    if match:
                        first_solana_coin = match.group()
                        if first_solana_coin not in self.solana_coins:
                            self.solana_coins.add(first_solana_coin)
                            solana_results.append(first_solana_coin)
        return tron_results, solana_results

    async def fill_coins_db(self, chat_id):
        logger.info(f"Заполнение базы данных монет из чата {chat_id}")
        messages = await self.__get_last_messages(chat_id)
        await self.parse_coins(messages)
        logger.info(f'TRON: {self.tron_coins}')
        logger.info(f'SOLANA: {self.solana_coins}')

    async def on_new_message(self, _, message):
        logger.info("Получено новое сообщение")
        caption = message.caption if message.caption else ""
        text = message.text if message.text else ""
        tron_coins, solana_coins = await self.parse_coins([caption + text])
        if tron_coins:
            logger.info(f"Новая TRON монета: {tron_coins[0]}")
            await self.client.send_message(chat_id="me", text=f"Новая TRON монета: {tron_coins[0]}")
            self.coin_type = 'Tron'
            self.new_coin = tron_coins[0]
        elif solana_coins:
            logger.info(f"Новая SOLANA монета: {solana_coins[0]}")
            await self.client.send_message(chat_id="me", text=f"Новая SOLANA монета: {solana_coins[0]}")
            self.coin_type = 'Solana'
            self.new_coin = solana_coins[0]
        self.message_received_event.set()
