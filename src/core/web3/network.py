from web3 import Web3
from web3.contract import Contract
from eth_typing.evm import Hash32
from eth_account import Account
from . import Network, Chain, Proxy
from ..types import Address, TxCall, Hash, Abi, PrivateKey, Connector
from ..exceptions import InvalidPrivateKey


class ProxyWeb3Contract(Proxy):
    _interface: Contract

    def __init__(self, interface: Contract):
        self._interface = interface

    def __getattr__(self, name: str):
        return getattr(self._interface.functions, name)


class Ethereum(Network):
    """Ethereum network type"""

    _web3: Web3
    _chain: Chain
    _connector: Connector

    def __init__(self, chain: Chain):
        self._connector = chain.provider()
        self._web3 = Web3(self._connector(chain.endpoint))
        self._chain = chain

    def set_default_account(self, private_key: PrivateKey):
        try:
            account = Account.from_key(private_key)
            self._web3.eth.default_account = account
        except ValueError as e:
            raise InvalidPrivateKey(str(e))

    def sign_transaction(self, tx: TxCall):
        return self._web3.eth.account.sign_transaction(
            tx, private_key=self._chain.private_key
        )

    def get_transaction(self, hash: Hash):
        assertion_hash = Hash32(hash)
        return self._web3.eth.get_transaction(assertion_hash)

    def send_transaction(self, tx: TxCall):
        # Return result from commit signed transaction
        signed_tx = self.sign_transaction(tx)
        transaction = signed_tx.rawTransaction
        return self._web3.eth.send_raw_transaction(transaction)

    def contract_factory(self, address: Address, abi: Abi):
        return ProxyWeb3Contract(
            self._web3.eth.contract(
                # Contract address
                address=Web3.toChecksumAddress(address),
                # Abi from contract deployed
                abi=abi,
            )
        )
