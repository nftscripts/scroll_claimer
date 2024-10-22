import json
from time import time

import pyuseragents
from loguru import logger

from src.models.contracts import ClaimContract
from src.utils.request_client.client import RequestClient
from src.utils.user.account import Account
from src.utils.wrappers.decorators import retry


class Scroll(Account, RequestClient):
    def __init__(
            self,
            private_key: str,
            proxy: str | None,
    ):
        Account.__init__(self, private_key=private_key, proxy=proxy)
        RequestClient.__init__(self, proxy=proxy)

    def __str__(self) -> str:
        return f'[{self.wallet_address}] | Claiming tokens...'

    async def get_claim_data(self):
        headers = {
            'accept': 'text/x-component',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'text/plain;charset=UTF-8',
            'next-action': '2ab5dbb719cdef833b891dc475986d28393ae963',
            'origin': 'https://claim.scroll.io',
            'priority': 'u=1, i',
            'referer': 'https://claim.scroll.io/?step=4',
            'user-agent': pyuseragents.random(),
        }

        data = f'["{self.wallet_address}"]'

        response_json = await self.make_request(
            method="POST",
            url='https://claim.scroll.io/?step=4',
            data=data,
            headers=headers,
        )

        json_objects = response_json.splitlines()
        json_object = json_objects[1]
        data = json.loads(json_object[2:])
        return data

    @retry(retries=3, delay=20, backoff=1.5)
    async def claim_tokens(self) -> None:
        data = await self.get_claim_data()
        if not data:
            logger.warning(f'[{self.wallet_address}] | Not eligible')
            return

        amount = int(data['amount'])
        claim_status = data['claim_status']
        if not claim_status == 'UNCLAIMED':
            logger.error(f'[{self.wallet_address}] | Already claimed')

        proof = data['proof']

        claim_contract = self.web3.eth.contract(
            address=ClaimContract.address,
            abi=ClaimContract.abi
        )

        tx = await claim_contract.functions.claim(
            self.wallet_address,
            amount,
            proof
        ).build_transaction({
            'value': 0,
            'nonce': await self.web3.eth.get_transaction_count(self.wallet_address),
            'from': self.wallet_address,
            'maxFeePerGas': int(await self.web3.eth.gas_price * 4),
            'maxPriorityFeePerGas': await self.web3.eth.gas_price
        })
        tx_hash = await self.sign_transaction(tx)
        confirmed = await self.wait_until_tx_finished(tx_hash)
        if confirmed:
            logger.success(f'Successfully claimed {amount / 10 ** 18} SCROLL tokens'
                           f' | TX: https://scrollscan.com/tx/{tx_hash}')
