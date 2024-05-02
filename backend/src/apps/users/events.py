from src.core.enums import StrEnum


class UserEventsEnum(StrEnum):

    USER_CREATED = "USER_CREATED"

    @classmethod
    def topics_list(cls):
        return [topic.value for topic in cls]
