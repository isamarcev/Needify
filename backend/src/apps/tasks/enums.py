from enum import Enum

from src.core.enums import StrEnum


class TaskStatusEnum(StrEnum):

    PRE_CREATED = 'PRE_CREATED'
    CREATED = 'CREATED'
    WAIT_FOR_EXECUTOR = 'WAIT_FOR_EXECUTOR'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    CONFIRMED = 'CONFIRMED'
    FINISHED = 'FINISHED'
    CANCELLED = 'CANCELLED'
    FAILED = 'FAILED'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

    @classmethod
    def values(cls):
        return [key.value for key in cls]

    @classmethod
    def mapping_rules_to_update_by_doer(cls) -> dict:
        return {
            cls.WAIT_FOR_EXECUTOR.value: [cls.IN_PROGRESS.value],
            cls.IN_PROGRESS.value: [cls.COMPLETED.value],
        }

    @classmethod
    def customer_active_statuses(cls) -> list[str]:
        return [cls.CREATED.value, cls.PRE_CREATED.value, cls.WAIT_FOR_EXECUTOR.value,
                cls.COMPLETED.value, cls.IN_PROGRESS.value]

    @classmethod
    def doer_active_statuses(cls) -> list[str]:
        return [cls.IN_PROGRESS.value, cls.COMPLETED.value, cls.CONFIRMED.value]

    @classmethod
    def done_statuses(cls) -> list[str]:
        return [cls.CONFIRMED.value, cls.FINISHED.value, cls.CANCELLED.value]

    @classmethod
    def mapping_rules_to_update_by_customer(cls) -> dict:
        return {
            cls.PRE_CREATED.value: [cls.CREATED.value],
            cls.CREATED.value: [cls.CANCELLED.value],
            cls.WAIT_FOR_EXECUTOR.value: [cls.CANCELLED.value],
            cls.COMPLETED.value: [cls.CONFIRMED.value],
        }

