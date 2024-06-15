from src.core.enums import StrEnum


class TaskStatusEnum(StrEnum):
    PRE_CREATED = "PRE_CREATED"
    PRE_DEPLOYING = "PRE_DEPLOYING"
    DEPLOYING = "DEPLOYING"
    PUBLISHED = "PUBLISHED"
    CLOSED = "CLOSED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CONFIRMED = "CONFIRMED"
    FINISHED = "FINISHED"
    REVOKED = "REVOKED"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

    @classmethod
    def values(cls):
        return [key.value for key in cls]

    @classmethod
    def could_be_revoked(cls) -> list[str]:
        return [
            cls.PRE_CREATED.value,
            cls.PRE_DEPLOYING.value,
            cls.DEPLOYING.value,
            cls.PUBLISHED.value,
        ]


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
