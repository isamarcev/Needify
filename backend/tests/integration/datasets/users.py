from typing import TypedDict


class USER(TypedDict):
    username: str
    telegram_id: int
    first_name: str
    last_name: str
    image: str
    web3_wallet: str


POSTER_DATA = {
    "username": "poster",
    "telegram_id": 123456,
    "first_name": "Poster",
    "last_name": "Poster",
    "image": "poster_image",
    "web3_wallet": "0QBVxO80__1rBGqrWzJjbMf5ZLmk0zyh3cps4vhl8ItwboL_",
}

POSTER = USER(**POSTER_DATA)
