import json

with open('data/abi/faucet_abi.json', 'r') as file:
    FAUCET_ABI = json.load(file)

with open('data/abi/erc_20_abi.json', 'r') as file:
    ERC_20_ABI = json.load(file)

with open('data/abi/hyperLend_pool.json', 'r') as file:
    HYPERLEND_POOL_ABI = json.load(file)

headers = {
                'authority': 'api.hyperlend.finance',
                'method': 'POST',
                "path": "",
                "scheme": "https",
                'Accept': 'application/json',
                'Accept-Language': 'en-US',
                'connection': 'keep-alive',
                'Origin': 'https://testnet.hyperlend.finance',
                'Referer': 'https://testnet.hyperlend.finance/',
                'User-Agent': "",
            }

# --------------------------------- FAUCET -----------------------------------------------

two_captcha_api_key = 'YOUT_2CAPTCHA_API_KEY'
SLEEP_MIN = 1  # faucet sleep min
SLEEP_MAX = 10 # faucet sleep max

# --------------------------------- TESTNET -----------------------------------------------

rpc = 'https://testnet.hyperlend.finance'

TESTNET_SLEEP_MIN = 1 # testnet sleep min
TESTNET_SLEEP_MAX = 60 # testnet sleep max

contracts = {
    'token_mockBTC': '0x453b63484b11bbF0b61fC7E854f8DAC7bdE7d458',
    'mockBTC_faucet': '0x941559af458a9a0448b411a26047584b506283a7',
    'HyperLend_pool': '0x1e85CCDf0D098a9f55b82F3E35013Eda235C8BD8',
    'HyperLend: Variable Debt MBTC': '0x742d75d7389E66f6C17898A0e19077E17F1C51d1',
    'HyperLend: Lend hMBTC': '0xde72990638db12f8AA4cd9406bA6c648153A5cEA'
}