from loguru import logger as ll
import requests
import time
from data_manager import DataManager
import fake_useragent
from config import two_captcha_api_key
class HyperLand:
    def __init__(self, address):
        self.address = address
        self.url = "https://testnet.hyperlend.finance/dashboard"
        self.captcha_token = '0x4AAAAAAA2Qg1SB87LOUhrG'
        self.CAPTCHA_API_KEY = two_captcha_api_key
        self.UA = fake_useragent.UserAgent().random
        self.session = requests.session()
        self.Data = DataManager()
        self.proxy = self.Data.get_proxy()

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

    def faucet(self):
        self.get_account_session()
        token = self.reCaptchaV2()
        if token == False:
            return False
        url = 'https://api.hyperlend.finance/ethFaucet'
        headers = {
            'authority': 'api.hyperlend.finance',
            'method': 'POST',
            "path": "/ethFaucet",
            "scheme": "https",
            'Accept': 'application/json',
            'Accept-Language': 'en-US',
            'connection': 'keep-alive',
            'Origin': 'https://testnet.hyperlend.finance',
            'Referer': 'https://testnet.hyperlend.finance/',
            'User-Agent': self.UA,
        }
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
                    ll.warning(f"Address [{self.address}] {response.json().get('response')}")
                elif response.json().get('response').get('status') == 1:
                    ll.success(f"Address [{self.address}] tokens received")
            else:
                ll.error(f"Status code {response.status_code}")
        except Exception as err:
            ll.error(err)
            return False


