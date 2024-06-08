import enum


class JobOfferOperationCodes(enum.IntEnum):
    REVOKE = 287
    GET_JOB = 335
    COMPLETE_JOB = 351
    CONFIRM_JOB = 367
    APPEAL = 383
    REVOKE_APPEAL = 399
    CONFIRM_APPEAL = 415

    CHOOSE_DOER = 559
