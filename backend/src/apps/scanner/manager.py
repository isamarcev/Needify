import asyncio
from abc import ABC
from pprint import pprint

from pytonlib import TonlibClient

from src.apps.utils.development import write_to_file
from src.core.producer import KafkaProducer


class BaseScanner(ABC):
    def infinity_scanner_process(self, *args, **kwargs):
        pass


class ScannerManager(BaseScanner):
    def __init__(
        self,
        lt_server_provider: TonlibClient,
        # toncenter_provider,
        # cache_database: BaseCacheDatabase,
        producer: KafkaProducer,
    ):
        self.lt_server_provider = lt_server_provider
        # self.toncenter_provider = toncenter_provider
        # self.cache_database = cache_database
        self.producer = producer

    async def get_last_network_block(self):
        masterchain_info = await self.lt_server_provider.get_masterchain_info()
        print(masterchain_info)
        return masterchain_info["last"]

    async def get_last_masterchain_seqno(self):
        masterchain_info = await self.lt_server_provider.get_masterchain_info()
        return masterchain_info["seqno"]

    async def get_masterchain_shards(self, masterchain_seqno: int):
        return await self.lt_server_provider.get_shards(masterchain_seqno)

    async def infinity_scanner_process(self, *args, **kwargs):
        last_node_block = await self.get_last_masterchain_seqno()
        print(last_node_block)
        last_scanned_block = await self.cache_database.get_last_scanned_block()
        if last_scanned_block is None:
            await self.cache_database.set_last_scanned_block(last_node_block)
            last_scanned_block = await self.cache_database.get_last_scanned_block()
        if last_scanned_block < last_node_block:
            shards = await self.get_masterchain_shards(last_scanned_block)
            print(shards, "shards")

    async def get_block_transactions(self, workchain, shard, seqno):
        return (
            await self.lt_server_provider.get_block_transactions(
                workchain, shard, seqno, count=1000
            )
        )["transactions"]

    async def scan_last_block_masterchain(self):

        last_masterchain_block = await self.get_last_network_block()
        last_masterchain_seqno = last_masterchain_block["seqno"]
        last_masterchain_seqno = 18790203
        print(last_masterchain_block)

        base_data = await self.lt_server_provider.get_shards(
            master_seqno=last_masterchain_seqno
        )
        print(base_data)

        shards = base_data["shards"]
        # pprint(shards)
        # shard = shards[0]
        # for shard in shards:
        detailed_transactions = []
        for shard in shards:
            # print(shard)
            # print(shard["workchain"], shard["shard"], shard["seqno"])
            #     print(shard)
            shard_transactions = await self.get_block_transactions(
                workchain=shard["workchain"], shard=shard["shard"], seqno=shard["seqno"]
            )
            pprint(shard_transactions)
            write_to_file("shard_transactions", shard_transactions)
            for tr in shard_transactions:

                full_tr = await self.lt_server_provider.get_transactions(
                    account=tr["account"],
                    from_transaction_lt=tr["lt"],
                    from_transaction_hash=tr["hash"],
                )
                detailed_transactions.append(full_tr)
        write_to_file("detailed_transactions", detailed_transactions)

    async def infinity_scanner(self):
        while True:
            # await self.producer.publish_message(WalletTopicsEnum.FOUNDED_DEPOSIT_WALLET, {"test": "test"})
            await asyncio.sleep(5)
            print("TEST INFINITY SCANNER")
