import random
import time
import questionary
from hyper_lend import HyperLend
from config import SLEEP_MIN, SLEEP_MAX, TESTNET_SLEEP_MAX, TESTNET_SLEEP_MIN

def choice():
    answers = questionary.select("Select what you want to do", choices=[
        questionary.Choice("HyperLend Faucet", 'faucet'),
        questionary.Choice("HyperLend Lend WBTC", 'lend'),
        questionary.Choice("HyperLend Borrow WBTC", 'borrow'),
        questionary.Choice("HyperLend Set Username", 'username')
    ],
    pointer="👉 "
    ).ask()
    return answers

if __name__ == '__main__':
    with open('data/wallets', 'r') as file:

        print("██╗░░██╗██╗░░░██╗██████╗░███████╗██████╗░██╗░░░░░███████╗███╗░░██╗██████╗░")
        print("██║░░██║╚██╗░██╔╝██╔══██╗██╔════╝██╔══██╗██║░░░░░██╔════╝████╗░██║██╔══██╗")
        print("███████║░╚████╔╝░██████╔╝█████╗░░██████╔╝██║░░░░░█████╗░░██╔██╗██║██║░░██║")
        print("██╔══██║░░╚██╔╝░░██╔═══╝░██╔══╝░░██╔══██╗██║░░░░░██╔══╝░░██║╚████║██║░░██║")
        print("██║░░██║░░░██║░░░██║░░░░░███████╗██║░░██║███████╗███████╗██║░╚███║██████╔╝" + '\n')
        print(f'👨‍🔧 Contact https://t.me/sol_wanker'+ "\n")
        wallets = [row.strip() for row in file]
        answer = choice()
        if answer == "faucet":
            for w in wallets:
                acc = HyperLend(w)
                acc.faucet()
                time.sleep(2)
                print("-----------------------------------------------------------------------------")
                time.sleep(random.randint(SLEEP_MIN, SLEEP_MAX))
        elif answer == "lend":
            for w in wallets:
                acc = HyperLend(w)
                if acc.lend():
                    time.sleep(random.randint(TESTNET_SLEEP_MIN, TESTNET_SLEEP_MAX))
                print("-----------------------------------------------------------------------------")
        elif answer == 'borrow':
            for w in wallets:
                acc = HyperLend(w)
                if acc.borrow():
                    time.sleep(random.randint(TESTNET_SLEEP_MIN, TESTNET_SLEEP_MAX))
                print("-----------------------------------------------------------------------------")
        elif answer == 'username':
            for w in wallets:
                acc = HyperLend(w)
                if acc.set_username():
                    time.sleep(random.randint(TESTNET_SLEEP_MIN, TESTNET_SLEEP_MAX))
                print("-----------------------------------------------------------------------------")
