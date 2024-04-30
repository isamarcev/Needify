from tonsdk.contract.token.ft import JettonMinter, JettonWallet
from tonsdk.utils import Address, to_nano
from src.core.config import config


def create_state_init_jetton():
    minter = JettonMinter(admin_address=Address(config.HD_WALLET_ADDRESS),
                          jetton_content_uri=config.NATIVE_JETTON_CONTENT_URL,
                          jetton_wallet_code_hex=JettonWallet.code)

    return minter.create_state_init()['state_init'], minter.address.to_string()


def increase_supply(amount_to_supply: int, destination: str = None):
    minter = JettonMinter(admin_address=Address(config.HD_WALLET_ADDRESS),
                          jetton_content_uri=config.NATIVE_JETTON_CONTENT_URL,
                          jetton_wallet_code_hex=JettonWallet.code,)

    body = minter.create_mint_body(destination=Address(destination or config.HD_WALLET_ADDRESS),
                            jetton_amount=to_nano(amount_to_supply, 'ton'))
    return body


def change_owner():
    minter = JettonMinter(admin_address=Address('EQB_bTCXmQpIldjAj5tGKKKl6p7JD-jDF0YQqmoyxffjgzCJ'),
                          jetton_content_uri='https://raw.githubusercontent.com/yungwine/pyton-lessons/master/lesson-6/token_data.json',
                          jetton_wallet_code_hex=JettonWallet.code)

    body = minter.create_change_admin_body(new_admin_address=Address('EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c'))
    return body