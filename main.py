import random
import time
import questionary
from hyper_land import HyperLand
from config import SLEEP_MIN, SLEEP_MAX

def choice():
    answers = questionary.select("Select what you want to do", choices=[
        questionary.Choice("HyperLand Faucet", 'faucet'),
        questionary.Choice("HyperLand TestNet", 'testnet')
    ],
    pointer="👉 "
    ).ask()
    return answers

if __name__ == '__main__':
    with open('data/wallets', 'r') as file:

        print("██╗░░██╗██╗░░░██╗██████╗░███████╗██████╗░██╗░░░░░░█████╗░███╗░░██╗██████╗░")
        print("██║░░██║╚██╗░██╔╝██╔══██╗██╔════╝██╔══██╗██║░░░░░██╔══██╗████╗░██║██╔══██╗")
        print("███████║░╚████╔╝░██████╔╝█████╗░░██████╔╝██║░░░░░███████║██╔██╗██║██║░░██║")
        print("██╔══██║░░╚██╔╝░░██╔═══╝░██╔══╝░░██╔══██╗██║░░░░░██╔══██║██║╚████║██║░░██║")
        print("██║░░██║░░░██║░░░██║░░░░░███████╗██║░░██║███████╗██║░░██║██║░╚███║██████╔╝")
        print("╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░░░░╚══════╝╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝╚═╝░░╚══╝╚═════╝░" + "\n \n")
        wallets = [row.strip() for row in file]
        answer = choice()
        if answer == "faucet":
            for w in wallets:
                acc = HyperLand(w)
                acc.faucet()
                time.sleep(random.randint(SLEEP_MIN, SLEEP_MAX))
                print("-----------------------------------------------------------------------------")
        elif answer == "testnet":
            print("testnet")