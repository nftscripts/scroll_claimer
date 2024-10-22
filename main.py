from asyncio import run, gather, create_task, sleep, set_event_loop_policy
import asyncio

import sys
import random
import logging

from loguru import logger

from src.utils.data.helper import private_keys, proxies, recipients
from config import PAUSE_BETWEEN_WALLETS, TRANSFER_AFTER_CLAIM
from src.claimer.claimer import Scroll
from src.utils.user.account import Account

if sys.platform == 'win32':
    set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.getLogger("asyncio").setLevel(logging.CRITICAL)


async def process_task(private_key: str, proxy: str) -> None:
    claimer = Scroll(
        private_key=private_key,
        proxy=f'http://{proxy}' if proxy else None
    )
    await claimer.claim_tokens()
    if TRANSFER_AFTER_CLAIM:
        await sleep(10)
        private_key_index = private_keys.index(private_key)
        recipient = recipients[private_key_index]

        account = Account(
            private_key=private_key,
            proxy=proxy
        )
        await account.transfer(recipient=recipient)


async def main() -> None:
    tasks = []
    proxy_index = 0
    for private_key in private_keys:
        proxy = proxies[proxy_index]
        proxy_index = (proxy_index + 1) % len(proxies)

        task = create_task(process_task(private_key, proxy))
        tasks.append(task)
        time_to_sleep = random.randint(PAUSE_BETWEEN_WALLETS[0], PAUSE_BETWEEN_WALLETS[1])
        logger.info(f'Sleeping {time_to_sleep} seconds...')
        await sleep(time_to_sleep)

    await gather(*tasks)


if __name__ == '__main__':
    run(main())
