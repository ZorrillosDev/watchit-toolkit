from . import chain
from .. import util
from ..constants import WALLET_KEY, PROJECT_ROOT
from ..exception import InvalidPrivateKey
from dataclasses import dataclass
from web3 import Web3


@dataclass
class Web3Wrapper:
    w3: Web3
    chain: str
    settings: dict

    def __init__(self, w3: Web3, chain: str, settings: None):
        self.w3 = w3
        self.chain = chain
        self.settings = settings


# TODO test this
def account(_w3: Web3, private_key: str = WALLET_KEY):
    """Returns wrapped account from private key

    :param web: Web3 instance
    :param private_key: wallet key address
    :return: account object
    :rtype: web3.Account
    """
    if not private_key:
        raise InvalidPrivateKey()

    return _w3.eth.account.privateKeyToAccount(private_key)


def w3(chain_name: str):
    """Build Web3 interface with provider settings

    :param chain_name: kovan, mainnet, rinkeby...
    :return: web3 interface with provider settings
    :rtype: Web3Wrapper
    """
    # Get chain settings from chain name
    chain_settings = chain.get_network_settings_by_name(chain_name)
    private_key = chain_settings.get("private_key")

    # Connect to provider based on chain settings
    _w3 = Web3(chain_settings.get("connect")())
    # Set default account for current WALLET_KEY settings
    _w3.eth.default_account = account(_w3, private_key)
    return Web3Wrapper(_w3, chain_name, chain_settings)


def nft_contract(w3_wrapper: Web3Wrapper, abi_path: str = PROJECT_ROOT):
    """Factory NFT contract based on provider settings

    :param chain_name: kovan, mainnet, rinkeby...
    :return: w3 interface, nft contract
    :rtype: Union[Web3, web3.eth.Contract]
    """
    # Get contract address based on chain settings
    chain_contract_nft = w3_wrapper.settings.get("nft")
    abi = util.read_json("%s/abi/WNFT.json" % abi_path)

    # web3 contract factory
    contract = w3_wrapper.w3.eth.contract(
        # Contract address
        address=Web3.toChecksumAddress(chain_contract_nft),
        # Abi from contract deployed
        abi=abi.get("abi"),
    )

    return w3_wrapper.w3, contract
