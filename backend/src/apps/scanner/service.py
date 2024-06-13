import asyncio
import logging

from pytoniq.liteclient import LiteClient
from pytoniq_core import Address, Transaction
from pytoniq_core.tl import BlockIdExt

from src.apps.tasks.manager import TaskManager
from src.apps.job_offer.manager import JobOfferManager
from src.core.local_storage import LocalStorage
from src.core.producer import BaseProducer


class BlockScanner:
    def __init__(
        self,
        lite_client: LiteClient,
        local_storage: LocalStorage,
        task_manager: TaskManager,
        job_offer_manager: JobOfferManager,
        producer: BaseProducer,
    ):
        self.lite_client = lite_client
        self.local_storage = local_storage
        self.task_manager = task_manager
        self.job_offer_manager = job_offer_manager
        self.producer = producer

    async def get_master_block_for_scan(self):
        last_scanned_block = await self.local_storage.get_last_scanned_block()
        master_blk: BlockIdExt = self.mc_info_to_tl_blk(
            await self.lite_client.get_masterchain_info()
        )
        if last_scanned_block is None:
            return master_blk
        if last_scanned_block < master_blk.seqno:
            master_blk, _ = await self.lite_client.lookup_block(
                wc=-1, shard=-9223372036854775808, seqno=last_scanned_block + 1
            )
            return master_blk
        logging.info("No new blocks to scan")
        return None

    async def manual_scan(self, mc_seqno: int):
        master_blk, _ = await self.lite_client.lookup_block(
            wc=-1, shard=-9223372036854775808, seqno=mc_seqno
        )
        shards = await self.lite_client.get_all_shards_info(master_blk)
        for shard in shards:
            await self.handle_block(shard)

    async def run(self):
        logging.info("Starting scanner")
        # return
        if not self.lite_client.inited:
            raise Exception("should init client first")
        while True:
            try:
                logging.error("Scanning...")
                master_blk = await self.get_master_block_for_scan()
                logging.error(f"{master_blk=}")
                if master_blk is None:
                    await asyncio.sleep(1)
                    continue
                shards = await self.lite_client.get_all_shards_info(master_blk)
                for shard in shards:
                    try:
                        await self.handle_block(shard)
                    except Exception as e:
                        logging.error(f"Error handling block: {e}")
                await self.local_storage.set_last_scanned_block(master_blk.seqno)
                logging.error(f"Scanned block {master_blk.seqno}")
            except Exception as e:
                logging.error(f"Error scanning: {e}")

    @staticmethod
    def mc_info_to_tl_blk(info: dict):
        return BlockIdExt.from_dict(info["last"])

    async def handle_block(self, block: BlockIdExt):
        if block.workchain == -1:  # skip masterchain blocks
            return
        transactions = await self.lite_client.raw_get_block_transactions_ext(block)
        for tx in transactions:
            tx: Transaction
            task_ = await self.task_manager.get_task_by_job_offer_address(
                Address(f"0:{tx.account_addr_hex}")
            )
            if task_ is not None:
                await self.job_offer_manager.process_job_offer_transaction(tx, task_)
                logging.info(f"Detected task for job offer address: 0:{tx.account_addr_hex}")
        logging.info(
            f"Block workchain: {block.workchain}, shard {block.shard}, {block.seqno=} handled"
        )
