import random

from web3 import Web3
from eth_account import Account as EthereumAccount
from loguru import logger as ll
from config import ERC_20_ABI

class Account:
    def __init__(self, pk):
        self.pk = pk
        self.w3 = Web3(Web3.HTTPProvider('https://api.hyperliquid-testnet.xyz/evm'))
        self.account = EthereumAccount.from_key(self.pk)
        self.address = self.account.address

    def get_contract(self, contract_address: str, abi=None):
        contract_address = self.w3.to_checksum_address(contract_address)
        if abi is None:
            ll.error('NO ABI')
        contract = self.w3.eth.contract(address=contract_address, abi=abi)

        return contract

    def check_allowance(self, token_address: str, contract_address: str) -> float:
        token_address = self.w3.to_checksum_address(token_address)
        contract_address = self.w3.to_checksum_address(contract_address)

        contract = self.w3.eth.contract(address=token_address, abi=ERC_20_ABI)
        amount_approved = contract.functions.allowance(self.address, contract_address).call()

        return amount_approved

    def approve(self, amount: int, token_address: str, contract_address: str):
        token_address = self.w3.to_checksum_address(token_address)
        contract_address = self.w3.to_checksum_address(contract_address)

        contract = self.w3.eth.contract(address=token_address, abi=ERC_20_ABI)

        allowance_amount = self.check_allowance(token_address, contract_address)

        if amount > allowance_amount or amount == 0:
            approve_amount = 2 ** 128 if amount > allowance_amount else 0
            tx_data = self.get_tx_data()
            transaction = contract.functions.approve(
                contract_address,
                approve_amount
            ).build_transaction(tx_data)

            signed_txn = self.sign(transaction)

            txn_hash = self.send_raw_transaction(signed_txn)
            self.w3.eth.wait_for_transaction_receipt(txn_hash)
            ll.info(f"[{self.address}] Approve https://testnet.purrsec.com/tx/{txn_hash.hex()}")

    def check_balance(self):
        balance = self.w3.eth.get_balance(self.address)
        return balance

    def get_balance(self, contract_address: str):
        contract_address = self.w3.to_checksum_address(contract_address)
        contract = self.get_contract(contract_address, abi=ERC_20_ABI)
        balance_wei = contract.functions.balanceOf(self.address).call()
        return balance_wei

    def get_tx_data(self, value: int = 0):
        tx = {
            "chainId": self.w3.eth.chain_id,
            "from": self.address,
            "value": 0,
            "gasPrice": int(self.w3.eth.gas_price * 1.5),
            "nonce": self.w3.eth.get_transaction_count(self.address),
        }
        return tx

    def sign(self, transaction):
        gas = int(self.w3.eth.estimate_gas(transaction) * 1.5)
        transaction.update({"gas": gas})
        signed_txn = self.w3.eth.account.sign_transaction(transaction, self.pk)
        return signed_txn

    def send_raw_transaction(self, signed_txn):
        txn_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        self.w3.eth.wait_for_transaction_receipt(txn_hash)
        return txn_hash