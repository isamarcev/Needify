from src.core.database import USDT_CURRENCY
from tests.integration.datasets.users import POSTER

task_data = {
    "title": "Test task",
    "description": "Test description",
    "category": "Test category",
    "images": ["test_image"],
    "price": 100.0,
    "currency": USDT_CURRENCY["symbol"],
    "poster_id": POSTER["telegram_id"],
    "deadline": "2022-01-01T00:00:00",
}
