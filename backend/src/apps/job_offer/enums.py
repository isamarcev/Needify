import enum


class JobOfferOperationCodes(enum.IntEnum):
    DEPLOY = 0x946A98B6
    TAKE_WALLET_ADDRESS = 0xD1735400
    REVOKE = 287
    GET_JOB = 335
    COMPLETE_JOB = 351
    CONFIRM_JOB = 367
    APPEAL = 383
    REVOKE_APPEAL = 399
    CONFIRM_APPEAL = 415
    CHOOSE_DOER = 559


class JobOfferChainStates(enum.IntEnum):
    PUBLISHED = 1
    PRE_PUBLISHED = 7
    CREATED = 0
    ACCEPTED = 2
    COMPLETED = 3
    CONFIRMED = 4
    APPEALED = 5
    CLOSED = 6
