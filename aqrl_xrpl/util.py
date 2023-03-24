from xrpl.clients import JsonRpcClient
from xrpl.clients import WebsocketClient
from xrpl.wallet import Wallet


JSON_RPC_URL_ALTNET = "https://s.altnet.rippletest.net:51234/"
JSON_RPC_URL_PROD = "https://s2.ripple.com:51234/"
WSS_RPC_URL_DEVNET = "wss://s.devnet.rippletest.net:51233/"

DEVNET_WALLET_ADDRESS = "rp5KSdgxuyJANWMu8dwsgMghs9txGYxcor"
DEVNET_WALLET_SECRET = "sEdV9Wm36f58CQdw8HMRziumaF9EUvw"
DEVNET_WALLET_SEQUENCE = 27151922
TESTNET_WALLET_ADDRESS = "rEh1oPPtYAAxi7yqfMmCMa4B84F26UHMtc"
TESTNET_WALLET_SECRET = "sEdScpfM43aE45wvkS5Umx215SL4Axc"
TESTNET_WALLET_SEQUENCE = 36413208

def get_devnet_wallet():
    return Wallet(seed=DEVNET_WALLET_SECRET, sequence=DEVNET_WALLET_SEQUENCE)

def get_network_url(mode: str) -> str:
    """Get a prod, altnet or devnet network url"""
    if mode == 'prod':
        return JSON_RPC_URL_PROD
    elif mode == 'altnet':
        return JSON_RPC_URL_ALTNET
    else:
        return WSS_RPC_URL_DEVNET

def get_client(mode: str):
    """Get a prod, altnet or devnet network client"""
    if mode == 'prod':
        return JsonRpcClient(JSON_RPC_URL_PROD)
    elif mode == 'altnet':
        return JsonRpcClient(JSON_RPC_URL_ALTNET)
    else:
        return WebsocketClient(WSS_RPC_URL_DEVNET)



