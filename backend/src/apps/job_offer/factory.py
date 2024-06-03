from src.apps.currency.schemas import CurrencySchema
from src.apps.job_offer.job_offer_contract import JobOfferContract
from src.apps.tasks.schemas import TaskSchema


class JobOfferFactory:
    async def create_job_offer(
        self,
        task_schema: TaskSchema,
        native_currency: CurrencySchema,
        master_currency: CurrencySchema,
    ):
        int_token_price = int(task_schema.price * 10**master_currency.decimals)
        job_offer = JobOfferContract(
            task_id=task_schema.task_id,
            title=task_schema.title,
            description=task_schema.description,
            price=int_token_price,
            jetton_master=master_currency.address,
            native_master=native_currency.address,
        )
        return job_offer
