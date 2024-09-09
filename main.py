import asyncio

from constants import API_HASH, API_ID
from loguru import logger
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from telegram.client import TelegramClient
from tron.client import TronClient

logger.add("info.log", format="{time} {level} {message}", level="INFO")


async def main():
    logger.info("Запуск основной функции")
    tg_client = TelegramClient(api_hash=API_HASH,
                               api_id=API_ID,
                               phone_number='+79635763362',
                               chat_id='testbotkik')
    tron_client = TronClient()
    logger.info('Инициализация TronClient')
    await tg_client.start()
    logger.info("Инициализация TelegramClient")

    # Получение уникальных TRON адресов из последних 20 сообщений
    await tg_client.fill_coins_db(tg_client.chat_id)
    logger.info("База данных монет заполнена из чата Telegram")
    await tron_client.fill_wallet_info()
    logger.info("Информация о кошельке Tron получена")

    # Подключение обработчика для новых сообщений
    tg_client.client.add_handler(MessageHandler(tg_client.on_new_message, filters.chat(tg_client.chat_id)))
    logger.info("Добавлен обработчик сообщений для новых сообщений")

    try:
        while True:
            logger.info("Ожидание новых сообщений")
            await tg_client.message_received_event.wait()
            if tg_client.coin_type == "Tron":
                coin = tg_client.new_coin
                tg_client.coin_type = None
                tg_client.new_coin = None
                await tron_client.buy_token(coin)
                await tron_client.get_buy_price(coin)
                #await tron_client.approve_token(coin)
                while True:
                    result = await tron_client.wait_for_sell(coin)
                    print(f'result: {result}')
                    if result == 'dump':
                        await tron_client.sell_token(coin, 1)
                        token_balance = await tron_client.get_coin_balance(coin)
                        tron_client.token_balance = token_balance
                    elif result == '2x':
                        await tron_client.sell_token(coin, 0.75)
                        token_balance = await tron_client.get_coin_balance(coin)
                        tron_client.token_balance = token_balance
                    elif result == '3x':
                        await tron_client.sell_token(coin, 1)
                        token_balance = await tron_client.get_coin_balance(coin)
                        tron_client.token_balance = token_balance
                    if tron_client.token_balance < 1:
                        trx_balance = await tron_client.get_trx_balance()
                        logger.success(f"Продал все монеты: "
                                       f"Прежний баланс: {tron_client.trx_balance['OnStart']} "
                                       f"Текущий баланс: {trx_balance} "
                                       f"Прибыль: {trx_balance - tron_client.trx_balance['OnStart']} TRX")
                        break
            elif tg_client.coin_type == "Solana":
                logger.info('Пока не поддерживаю Solana')
            else:
                logger.info('Неизвестный тип монеты')
            tg_client.message_received_event.clear()
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        # Сброс состояния события, чтобы можно было снова ждать следующего
        tg_client.message_received_event.clear()

    finally:
        await tg_client.stop()
        logger.info("Telegram клиент остановлен")


async def test():
    tron_client = TronClient()
    await tron_client.fill_wallet_info()
    logger.info("Информация о кошельке Tron получена")
    coin = 'TNP9AtSryuYLqufUs9LNNxnv8VK8r1Yg4o'
    tron_client.token_balance = await tron_client.get_coin_balance(coin)
    await tron_client.sell_token(coin, 0.75)
    #164400

if __name__ == "__main__":
    asyncio.run(main())
