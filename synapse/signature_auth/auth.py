import logging
import time

from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3

from synapse.module_api import ModuleApi


log = logging.getLogger(__name__)


class SignatureAuth:
    def __init__(self, config, account_handler: ModuleApi):
        self.api = account_handler
        self.config = config
        account_handler.register_password_auth_provider_callbacks(
            auth_checkers={
                ("login.signature", ("signature",)): self.check_my_login,
            },
        )

    @staticmethod
    def parse_config(config):
        return config

    async def check_my_login(
        self,
        username: str,
        login_type: str,
        login_dict: "synapse.module_api.JsonDict",
        *args, **kwargs
    ):
        message_encoded = encode_defunct(text=self.config["message"])
        signature = login_dict["signature"]
        signer_address = Account.recover_message(message_encoded, signature=signature).lower()
        username = self.api.get_qualified_user_id(signer_address)
        users = await self.api._hs.get_registration_handler().store.get_users_by_id_case_insensitive(username)
        if not users:
            await self.api.register_user(signer_address)
        return (username, None)

