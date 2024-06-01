from src.core.enums import StrEnum


class TaskStatusEnum(StrEnum):

    PRE_CREATED = "PRE_CREATED"
    DEPLOYING = "DEPLOYING"
    PUBLISHED = "PUBLISHED"
    CLOSED = "CLOSED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CONFIRMED = "CONFIRMED"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

    @classmethod
    def values(cls):
        return [key.value for key in cls]

    # @classmethod
    # def mapping_rules_to_update_by_doer(cls) -> dict:
    #     return {
    #         cls.WAIT_FOR_EXECUTOR.value: [cls.IN_PROGRESS.value],
    #         cls.IN_PROGRESS.value: [cls.COMPLETED.value],
    #     }

    # @classmethod
    # def customer_active_statuses(cls) -> list[str]:
    #     return [
    #         cls.CREATED.value,
    #         cls.PRE_CREATED.value,
    #         cls.WAIT_FOR_EXECUTOR.value,
    #         cls.COMPLETED.value,
    #         cls.IN_PROGRESS.value,
    #     ]
    #
    # @classmethod
    # def doer_active_statuses(cls) -> list[str]:
    #     return [cls.IN_PROGRESS.value, cls.COMPLETED.value, cls.CONFIRMED.value]
    #
    # @classmethod
    # def done_statuses(cls) -> list[str]:
    #     return [cls.CONFIRMED.value, cls.FINISHED.value, cls.CANCELLED.value]
    #
    # @classmethod
    # def mapping_rules_to_update_by_customer(cls) -> dict:
    #     return {
    #         cls.PRE_CREATED.value: [cls.CREATED.value],
    #         cls.CREATED.value: [cls.CANCELLED.value],
    #         cls.WAIT_FOR_EXECUTOR.value: [cls.CANCELLED.value],
    #         cls.COMPLETED.value: [cls.CONFIRMED.value],
    #     }






class JobOfferMessagesEnum(StrEnum):
    DEPLOY = "DEPLOY"
    GET_JOB = "GET_JOB"
    CHOOSE_DOER = "CHOOSE_DOER"
    COMPLETE_JOB = "COMPLETE_JOB"
    CONFIRM_JOB = "CONFIRM_JOB"
    REVOKE = "REVOKE"
    APPEAL = "APPEAL"


class JobOfferPlatformMessagesEnum(StrEnum):
    CHECK_PUBLISH = "CHECK_PUBLISH"


class AppealMessagesEnum(StrEnum):
    DEPLOY = "DEPLOY"
    BE_JUDGE = "BE_JUDGE"
    VOTE = "VOTE"
    REVOKE = "REVOKE"
    CONFIRM_APPEAL = "CONFIRM_APPEAL"
