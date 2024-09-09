import asyncio
import json
import os
import time

from constants import (BASE58_TRX, HEX_TRX, INFINITY_VALUE, PRIVATE_KEY,
                       ROUTER_ADDRESS)
from loguru import logger
from tronpy import AsyncTron
from tronpy.keys import PrivateKey
from tronpy.providers.async_http import AsyncHTTPProvider

abi_dir = os.path.dirname(os.path.abspath(__file__))


def load_abi(filename):
    abi_path = os.path.join(abi_dir, filename)
    with open(abi_path, 'r') as file:
        abi = json.load(file)
    return abi


class TronClient:
    def __init__(self):
        self.client = AsyncTron(AsyncHTTPProvider('https://api.trongrid.io',
                                         api_key='ba71a06b-2923-4fa6-80b3-b3de992e022f'))
        self.wallet = PrivateKey(bytes.fromhex(PRIVATE_KEY))
        self.address = self.wallet.public_key.to_base58check_address()
        self.router_contract = None
        self.token_abi = load_abi('token_abi.json')
        self.trx_balance = {}
        self.token_balance = None
        self.buy_price = None
        self.max_price = None
        self.done2x = False

    async def get_trx_balance(self):
        logger.info(f"Получение баланса TRX для адреса {self.address}")
        try:
            account_info = await self.client.get_account(self.address)
            trx_balance = account_info['balance'] / 10 ** 6  # Convert from sun to TRX
            logger.info(f"Баланс TRX: {trx_balance}")
            return trx_balance
        except Exception as e:
            logger.error(f"Ошибка при получении баланса TRX: {e}")
            return None

    async def get_coin_balance(self, token_address):
        logger.info(f"Получение баланса токена {token_address}")
        try:
            token_contract = await self.client.get_contract(token_address)
            token_contract.abi = self.token_abi
            balance = await token_contract.functions.balanceOf(self.address)
            balance = balance / 10**18
            logger.info(f"Баланс токена {token_address}: {balance}")
            return balance
        except Exception as e:
            logger.error(f"Ошибка при получении баланса токена: {e}")
            return None

    async def get_buy_price(self, token_address):
        logger.info("Получение цены покупки")
        try:
            self.token_balance = await self.get_coin_balance(token_address)
            #print(f"Куплено токенов: {self.token_balance}")
            logger.info('Куплено токенов:', self.token_balance)
            trx_balance = await self.get_trx_balance()
            spent_money = self.trx_balance['OnStart'] - trx_balance
            #print(f"Потрачено денег: {spent_money}")
            logger.info('Потрачено на покупку:', spent_money)
            self.buy_price = spent_money / self.token_balance
            logger.info(f"Цена покупки: {self.buy_price:.6f}")
            return self.buy_price
        except Exception as e:
            logger.error(f"Ошибка при получении цены покупки: {e}")
            return None

    async def wait_for_sell(self, token_address):
        token_price_old = await self.get_price_to_token(token_address)
        self.max_price = token_price_old[0]
        logger.info(f'Цена покупки: {self.buy_price}')
        logger.info(f"Указал максимальную цену монеты: {self.max_price}")

        while True:
            token_price = await self.get_price_to_token(token_address)
            #print(f'token_price: {token_price[0]} | max_price: {self.max_price}')
            #print(f'percent: {token_price[0] / self.max_price}')
            #print(f'percent_buy: {token_price[0] / self.buy_price}')
            #print(f'Цена покупки: {self.buy_price}')
            growth_factor = token_price[0] / self.buy_price
            if token_price_old == token_price:
                pass
            elif token_price[0] > self.max_price:
                self.max_price = token_price[0]
                logger.success(f"Обновил максимальную цену монеты: {self.max_price}")
            elif (token_price[0] / self.max_price) < 0.75:
                logger.info("Продажа токена из-за снижения цены более чем на 75%")
                return 'dump'
            elif growth_factor > 1.2 and not self.done2x:
                logger.info("Продажа токена из-за роста цены более чем на 2x")
                self.done2x = True
                return '2x'
            elif growth_factor > 3:
                logger.info("Продажа токена из-за роста цены более чем на 3x")
                return '3x'
            logger.info(f"Токен изменился на {growth_factor:.4f}x")
            await asyncio.sleep(1.5)

    async def fill_wallet_info(self):
        self.trx_balance['OnStart'] = await self.get_trx_balance()
        self.router_contract = await self.client.get_contract(ROUTER_ADDRESS)

    async def get_price_to_token(self, token_address, token_amount=1):
        token_amount_converted = token_amount
        path = [BASE58_TRX, token_address]
        token_amount = int(token_amount * 10**6)
        token_price_raw = await (self.router_contract.functions.
                                 getAmountsOut(token_amount, path))
        tokens_get = token_price_raw[-1] / 10**18
        token_price = ((token_amount / 10**6) / tokens_get)
        logger.info(f"{token_address} | {token_amount_converted} TRX | {token_price:.8f}")
        return token_price, tokens_get

    async def approve_token(self, token_address):
        try:
            logger.info(f"Апрув токена {token_address}")
            token_contract = await self.client.get_contract(token_address)
            token_contract.abi = self.token_abi
            txb = await (
                token_contract.functions.approve.with_owner(self.address)(
                    ROUTER_ADDRESS,
                    INFINITY_VALUE)
            )
            txn = await txb.build()
            txn_ret = await txn.sign(self.wallet).broadcast()
            await txn_ret.wait(solid=True, timeout=120)
            result = await txn_ret.result()
            token_balance = await self.get_coin_balance(token_address)
            if result:
                logger.info(f"Токен {token_address} куплен | {token_balance} Tokens")
                logger.info(f"Токен {token_address} апрувнут")
                return True
        except Exception as e:
            logger.error(f"Ошибка при апруве токена: {e}")

    async def sell_token(self, token_address, percentage_sell, amount_out=1*10**6, slippage=0.7):
        try:
            amount_in = int(self.token_balance * percentage_sell)
            logger.info(f"Продажа токена {token_address} с количеством {amount_in}")
            token_price = await self.get_price_to_token(token_address)
            amount_out = int(amount_in * token_price[0] * slippage * 10**6)
            amount_in = int(amount_in * 10**18)
            txb = await (
                self.router_contract.functions.swapExactTokensForETH
                .with_owner(self.address)(
                      amount_in,
                        amount_out,
                        [token_address, BASE58_TRX],
                        self.address,
                        int(time.time() + 20)
                )
            )
            txn = await txb.build()
            txn_ret = await txn.sign(self.wallet).broadcast()
            await txn_ret.wait(solid=True, timeout=120)
            result = await txn_ret.result()
            if result:
                logger.info(f"Токен {token_address} продан")
                return True
        except Exception as e:
            logger.error(f"Ошибка при продаже токена: {e}")
            return None

    async def buy_token(self, token_address, percentage_buy=0.75):
        try:
            token_amount = int(self.trx_balance['OnStart'] * percentage_buy)
            logger.info(f"Покупка токена {token_address} на {token_amount} TRX")
            amountOutMin = await self.get_price_to_token(token_address)
            amountOutMin = int(amountOutMin[1] * 0.7)
            token_amount = int(token_amount * 10**6)
            path = [BASE58_TRX, token_address]
            deadline = int(time.time() + 20)
            txb = await (
                self.router_contract.functions.swapExactETHForTokens.with_transfer(token_amount)
                .with_owner(self.address)
                .call(amountOutMin, path, self.address, deadline)
            )
            txn = await txb.build()
            txn_ret = await txn.sign(self.wallet).broadcast()
            await txn_ret.wait(solid=True, timeout=120)
            result = await txn_ret.result()
            # token_balance = await self.get_coin_balance(token_address)
            if result:
                # logger.info(f"Токен {token_address} куплен | {token_balance} Tokens")
                return True

        except Exception as e:
            logger.error(f"Ошибка при покупке токена: {e}")
            return None
