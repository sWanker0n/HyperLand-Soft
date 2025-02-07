import random

from loguru import logger as ll
import requests
import time
from data_manager import DataManager
import fake_useragent
from config import two_captcha_api_key, FAUCET_ABI, contracts, headers, HYPERLEND_POOL_ABI
from account import Account
from eth_account.messages import encode_defunct
from faker import Faker



class HyperLend(Account):
    def __init__(self, pk):
        super().__init__(pk=pk)
        self.url = "https://testnet.hyperlend.finance/dashboard"
        self.captcha_token = '0x4AAAAAAA2Qg1SB87LOUhrG'
        self.CAPTCHA_API_KEY = two_captcha_api_key
        self.UA = fake_useragent.UserAgent().random
        self.session = requests.session()
        self.Data = DataManager()
        self.proxy = self.Data.get_proxy()

        self.faucet_contract = self.get_contract(contract_address=contracts['mockBTC_faucet'], abi=FAUCET_ABI)
        self.hyperLend_pool_contract = self.get_contract(contract_address=contracts["HyperLend_pool"], abi=HYPERLEND_POOL_ABI)


    def check_proxy(self):
        # FORMAT http://{proxy_username}:{proxy_password}@{http_proxy_url}
        url = 'https://jsonip.com'
        for i in range(1, 6):
            proxy = {
                'http': f'http://{self.proxy}',
                'https': f'http://{self.proxy}'
            }
            try:
                self.session.proxies = proxy

                response = self.session.get(url=url)
                if response.status_code == 200:
                    return True
                else:
                    ll.warning('Proxy Error')
                    self.proxy = self.Data.get_proxy()


            except Exception as err:
                ll.warning(f'{err}')
                self.proxy = self.Data.get_proxy()

        ll.error(f'changing proxy didnt help')
        return False

    def get_account_session(self):
        status = self.check_proxy()
        if status:
            return self.session
        else:
            return False


    def reCaptchaV2(self):
        for i in range(1, 3):
            try:
                url = 'https://api.2captcha.com/createTask'
                body = {
                    "clientKey": self.CAPTCHA_API_KEY,
                    "task": {
                        "type": "TurnstileTaskProxyless",
                        "websiteURL": self.url,
                        "websiteKey": self.captcha_token
                    }
                }
                response = self.session.post(url=url, json=body)
                response = response.json()
                if response.get('errorId') == 0:
                    url = 'https://api.2captcha.com/getTaskResult'

                    payload = {
                        "clientKey": self.CAPTCHA_API_KEY,
                        "taskId": response.get('taskId')
                    }

                    total_time = 0
                    timeout = 180
                    while True:
                        response = self.session.post(url=url, json=payload).json()

                        if response.get('status') == 'ready':
                            return response.get('solution').get('token')

                        total_time += 5
                        time.sleep(5)

                        if total_time > timeout:
                            ll.error("Can't solve the captcha ")
                            return False
                else:
                    ll.warning(f"{response.json()}")
                    time.sleep(5)
            except Exception as err:
                ll.warning(err)
                time.sleep(5)

        ll.error(f"Cant solve captcha")
        return False

    def request_mockBTC(self):
        if self.w3.is_connected():
            if self.check_balance() >= 50000000000000:
                try:
                    isClaimed = self.faucet_contract.functions.isClaimed(add=self.w3.to_checksum_address(self.address)).call()
                    if isClaimed:
                        ll.warning(f"[{self.address}] already claimed mockBTC")
                        return False
                    ll.info(f"[{self.address}] trying to claim mockBTC...")
                    tx_data = self.get_tx_data()
                    transaction = self.faucet_contract.functions.claim().build_transaction(tx_data)
                    signed_txn = self.sign(transaction)
                    txn_hash = f"0x{self.send_raw_transaction(signed_txn).hex()}"
                    ll.success(f"[{self.address}] https://testnet.purrsec.com/tx/{txn_hash}")
                except Exception as err:
                    ll.error(err)
                    return False

            else:
                ll.warning(f"[{self.address}] don't have enough HYPE balance ")
                return False

        else:
            ll.error("Cant connect to RPC")
            return False

    def faucet(self):
        self.get_account_session()
        ll.info(f"[{self.address}] trying to claim HYPER...")
        token = self.reCaptchaV2()
        if token == False:
            return False
        url = 'https://api.hyperlend.finance/ethFaucet'
        headers['path'] = "/ethFaucet"
        headers['User-Agent'] = self.UA
        body = {
            "challenge": token,
            "challengeV2": "If you are running the farming bot, stop wasting your time. Testnet will not be directly incentivized, and mainnet airdrop will be linear with a minimum threshold.",
            "type": "ethFaucet",
            "user": self.address
        }
        try:
            response = self.session.post(url=url, json=body, headers=headers)
            if response.status_code == 200:
                if response.json().get('response') == 'user_already_claimed':
                    ll.warning(f"[{self.address}] {response.json().get('response')} HYPER")
                    self.request_mockBTC()
                elif response.json().get('response').get('status') == 1:
                    ll.success(f"[{self.address}] tokens received")
                    sleep = random.randint(1, 20)
                    ll.info(f'Sleep {sleep} sec')
                    time.sleep(sleep)
                    self.request_mockBTC()
            else:
                ll.error(f"Status code {response.status_code}")
        except Exception as err:
            ll.error(err)
            return False

    def check_username(self):
        try:
            url = f'https://api.hyperlend.finance/leaderboard/name/get?address={self.address}'
            headers['path'] = f"/leaderboard/name/get?address={self.address}"
            headers['User-Agent'] = self.UA
            response = self.session.get(url=url, headers=headers)

            if response.json().get('name') == None:
                return True
            else:
                return False

        except Exception as err:
            ll.error(err)
            return False

    def set_username(self):
        fake = Faker()
        username = fake.user_name()
        status = self.check_username()

        if status == False:
            ll.warning(f"[{self.address}] username already registered")
            return False

        try:

            ll.info(f"[{self.address}] try to register username: {username}")
            text = f'hyperlend_leaderborad_name_{self.address.lower()}_{username}'
            message = encode_defunct(text=text)
            signed_message = self.w3.eth.account.sign_message(message, private_key=self.pk)
            signature = f"0x{signed_message.signature.hex()}"
            url = f'https://api.hyperlend.finance/leaderboard/name/set?address={self.address}&signature={signature}&name={username}'
            headers['path'] = f"leaderboard/name/set?address={self.address}&signature={signature}&name={username}"
            response = self.session.get(url=url, headers=headers)

            if response.json().get('msg') == 'name updated':
                ll.success(f'[{self.address}] successfully registered username: {username}')
            else:
                ll.warning(f'[{self.address}] status code {response.status_code}')

        except Exception as err:
            ll.error(err)

    def lend(self):
        try:
            if self.check_balance() >= 500000000000:
                btc_balance = self.get_balance(contract_address=contracts["token_mockBTC"])
                if btc_balance >= 1000000:
                    lend_amount = int(btc_balance * (random.randint(850, 950) / 1000))
                    ll.info(f"[{self.address}] try to lend {lend_amount / 10 ** 8 } WBTC")
                    self.approve(amount=self.w3.to_wei(random.randint(1, 1000) / 10, "ether"), token_address=contracts['token_mockBTC'], contract_address=contracts['HyperLend_pool'])
                    tx_data = self.get_tx_data()
                    transaction = self.hyperLend_pool_contract.functions.supply(token_address=self.w3.to_checksum_address(contracts['token_mockBTC']), amount=lend_amount, wallet_address=self.w3.to_checksum_address(self.address), something=0).build_transaction(tx_data)
                    signed_txn = self.sign(transaction)
                    txn_hash = f"0x{self.send_raw_transaction(signed_txn).hex()}"
                    ll.success(f"[{self.address}] lended https://testnet.purrsec.com/tx/{txn_hash}")
                    return True
                else:
                    ll.warning(f"[{self.address}] dont have enough mockBTC for lend")
                    return False
            else:
                ll.warning(f"[{self.address}] dont have enough HYPE balance to pay fees")
                return False
        except Exception as err:
            ll.error(err)
            return False

    def borrow(self):
        try:
            if self.check_balance() >= 500000000000:
                lend_btc_balance = self.get_balance(contract_address=contracts["HyperLend: Lend hMBTC"])
                borrowed_btc_balance = self.get_balance(contract_address=contracts["HyperLend: Variable Debt MBTC"])
                LVT = int(lend_btc_balance * 0.74) - borrowed_btc_balance
                if LVT >= 700000:
                    borrow_amount = int(LVT * (random.randint(900, 990)/1000))
                    ll.info(f"[{self.address}] try to borrow {borrow_amount / 10 ** 8 } WBTC")
                    tx_data = self.get_tx_data()
                    transaction = self.hyperLend_pool_contract.functions.borrow(token_address=self.w3.to_checksum_address(contracts['token_mockBTC']), amount=borrow_amount, something1=2, something2=0, wallet_address=self.w3.to_checksum_address(self.address)).build_transaction(tx_data)
                    signed_txn = self.sign(transaction)
                    txn_hash = f"0x{self.send_raw_transaction(signed_txn).hex()}"
                    ll.success(f"[{self.address}] borrowed https://testnet.purrsec.com/tx/{txn_hash}")
                    return True
                else:
                    ll.warning(f"[{self.address}] dont have enough LTV for borrowing, you need to lend more WBTC")
                    return False
            else:
                ll.warning(f"[{self.address}] dont have enough HYPE balance to pay fees")
                return False
        except Exception as err:
            ll.error(err)
            return False





