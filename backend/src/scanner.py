# noqa
import asyncio
from datetime import datetime
from pprint import pprint
from types import coroutine

from dotenv import load_dotenv

load_dotenv()
from pytoniq.liteclient import LiteClient  # noqa
from pytoniq_core import Transaction  # noqa
from pytoniq_core.boc.deserialize import Boc  # noqa
from pytoniq_core.tl import BlockIdExt  # noqa
from pytoniq_core.tlb.block import ExtBlkRef  # noqa

from src.core.provider import get_ton_lib_client  # noqa


async def log_transaction(ftx, identity: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {ftx}\n"

    # Открываем файл для дописывания данных
    with open(f"{identity}-transaction_log.txt", "a") as file:
        file.write(log_message)


class BlockScanner:
    def __init__(self, client: LiteClient, block_handler: coroutine):
        """
        :param client: LiteClient
        :param block_handler: function to be called on new block
        """
        self.client = client
        self.block_handler = block_handler
        self.shards_storage = {}
        self.blks_queue = asyncio.Queue()

    async def one_more_manual_scan(self, wc, shard, seqno):
        client = await get_ton_lib_client()
        txs = await self.get_block_transactions(client, wc, shard, seqno)
        # print(txs, "TXS")
        for tx in txs:
            full_tr = await client.get_transactions(
                account=tx["account"],
                from_transaction_lt=tx["lt"],
                from_transaction_hash=tx["hash"],
            )
            for ftx in full_tr:
                await log_transaction(ftx, identity=f"{wc}:{shard}:{seqno}")

    async def get_block_transactions(self, client, wc, shard, seqno):
        txs = await client.get_block_transactions(
            workchain=wc, shard=shard, seqno=seqno, count=1000
        )
        return txs["transactions"]

    async def manual_scan(self, mc_seqno: int | None = None):
        client = await get_ton_lib_client()
        last_master_seqno = 0
        while True:
            last_master_block = (await client.get_masterchain_info())["last"]
            if last_master_seqno == last_master_block["seqno"]:
                await asyncio.sleep(1)
                continue
            last_master_seqno = last_master_block["seqno"]
            # print(last_master_block)
            # get shards
            shards = (await client.get_shards(last_master_block["seqno"]))["shards"]
            print(shards)
            # return
            for shard in shards:
                # print(base_data
                #       )
                # return
                workchain = shard["workchain"]
                base_shard = shard["shard"]
                base_seqno = shard["seqno"]
                print(f"Scanning {workchain=}:{base_shard=}:{base_seqno=}")

                txs = await self.get_block_transactions(client, workchain, base_shard, base_seqno)
                # # print(txs)
                for tx in txs:
                    full_tr = await client.get_transactions(
                        account=tx["account"],
                        from_transaction_lt=tx["lt"],
                        from_transaction_hash=tx["hash"],
                    )
                    # print(full_tr)
                    for ftx in full_tr:
                        await log_transaction(
                            ftx, identity=f"{workchain}:{base_shard}:{base_seqno}"
                        )
        # print(txs)

    async def run(self, mc_seqno: int | None = None):
        if not self.client.inited:
            raise Exception("should init client first")

        if mc_seqno is None:
            master_blk: BlockIdExt = self.mc_info_to_tl_blk(
                await self.client.get_masterchain_info()
            )
        else:
            master_blk, _ = await self.client.lookup_block(
                wc=-1, shard=-9223372036854775808, seqno=mc_seqno
            )

        master_blk_prev, _ = await self.client.lookup_block(
            wc=-1, shard=-9223372036854775808, seqno=master_blk.seqno - 1
        )
        # print(master_blk, "master_blk")
        shards_prev = await self.client.get_all_shards_info(master_blk_prev)
        # print(shards_prev, "shards_prev")
        for shard in shards_prev:
            self.shards_storage[self.get_shard_id(shard)] = shard.seqno

        while True:
            await self.blks_queue.put(master_blk)

            shards = await self.client.get_all_shards_info(master_blk)
            for shard in shards:
                await self.get_not_seen_shards(shard)
                self.shards_storage[self.get_shard_id(shard)] = shard.seqno

            while not self.blks_queue.empty():
                await self.block_handler(self.blks_queue.get_nowait())

            while True:
                if master_blk.seqno + 1 == self.client.last_mc_block.seqno:
                    master_blk = self.client.last_mc_block
                    break
                elif master_blk.seqno + 1 < self.client.last_mc_block.seqno:
                    master_blk, _ = await self.client.lookup_block(
                        wc=-1, shard=-9223372036854775808, seqno=master_blk.seqno + 1
                    )
                    break
                await asyncio.sleep(0.1)

    async def get_not_seen_shards(self, shard: BlockIdExt):
        if self.shards_storage.get(self.get_shard_id(shard)) == shard.seqno:
            return

        full_blk = await self.client.raw_get_block_header(shard)
        prev_ref = full_blk.info.prev_ref
        if prev_ref.type_ == "prev_blk_info":  # only one prev block
            prev: ExtBlkRef = prev_ref.prev
            prev_shard = (
                self.get_parent_shard(shard.shard) if full_blk.info.after_split else shard.shard
            )
            await self.get_not_seen_shards(
                BlockIdExt(
                    workchain=shard.workchain,
                    seqno=prev.seqno,
                    shard=prev_shard,
                    root_hash=prev.root_hash,
                    file_hash=prev.file_hash,
                )
            )
        else:
            prev1: ExtBlkRef = prev_ref.prev1
            prev2: ExtBlkRef = prev_ref.prev2
            await self.get_not_seen_shards(
                BlockIdExt(
                    workchain=shard.workchain,
                    seqno=prev1.seqno,
                    shard=self.get_child_shard(shard.shard, left=True),
                    root_hash=prev1.root_hash,
                    file_hash=prev1.file_hash,
                )
            )
            await self.get_not_seen_shards(
                BlockIdExt(
                    workchain=shard.workchain,
                    seqno=prev2.seqno,
                    shard=self.get_child_shard(shard.shard, left=False),
                    root_hash=prev2.root_hash,
                    file_hash=prev2.file_hash,
                )
            )

        await self.blks_queue.put(shard)

    def get_child_shard(self, shard: int, left: bool) -> int:
        x = self.lower_bit64(shard) >> 1
        if left:
            return self.simulate_overflow(shard - x)
        return self.simulate_overflow(shard + x)

    def get_parent_shard(self, shard: int) -> int:
        x = self.lower_bit64(shard)
        return self.simulate_overflow((shard - x) | (x << 1))

    @staticmethod
    def simulate_overflow(x) -> int:
        return (x + 2**63) % 2**64 - 2**63

    @staticmethod
    def lower_bit64(num: int) -> int:
        return num & (~num + 1)

    @staticmethod
    def mc_info_to_tl_blk(info: dict):
        return BlockIdExt.from_dict(info["last"])

    @staticmethod
    def get_shard_id(blk: BlockIdExt):
        return f"{blk.workchain}:{blk.shard}"


async def handle_block(block: BlockIdExt):
    if block.workchain == -1:  # skip masterchain blocks
        return
    transactions = await client.raw_get_block_transactions_ext(block)
    for tx in transactions:
        tx: Transaction
        print(tx.account_addr)
        print(tx.description)
        print(tx.in_msg)
        print(tx.out_msgs)
        print(tx.total_fees)
        print(tx.orig_status)

        print("Transaction: \n")
        pprint(tx)
    print(f"{len(transactions)=}")
    # for transaction in transactions:
    #     print(transaction.in_msg)


client = LiteClient.from_testnet_config(ls_i=3, trust_level=2, timeout=20)


async def main():
    await client.connect()
    await client.reconnect()
    await BlockScanner(client=client, block_handler=handle_block).one_more_manual_scan(
        0, 6917529027641081856, 20372994
    )
    # await BlockScanner(client=client, block_handler=handle_block).manual_scan(None)


if __name__ == "__main__":
    asyncio.run(main())
