from functools import wraps
from .blockchain import Blockchain
from .utils.validator import Validator
from .wallet import Wallet


class Node:
    def __init__(self):
        self.wallet = Wallet()
        self.create_wallet()

    def print_wrapper(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            print('-' * 30)
            func(self, *args, **kwargs)
            print('-' * 30)
        return wrapper

    @print_wrapper
    def print_blockchain(self):
        for block in self.blockchain.chain:
            print('Outputting block: ')
            print(block)

    @print_wrapper
    def print_balance(self):
        print('Balance of user {}: {:6.2f}'
              .format(self.wallet.public_key, self.blockchain.get_balance()))

    def get_transaction_info(self):
        tx_recipient = input('Enter the recipient of the transaction: ')
        tx_amount = float(input('Please pass transaction amount: '))
        return (tx_recipient, tx_amount)

    def get_user_choice(self):
        return input('Your choice: ')

    def initialize_blockchain(self, hosting_node):
        self.blockchain = Blockchain(hosting_node)

    def create_wallet(self):
        self.wallet.create_keys()
        self.initialize_blockchain(self.wallet.public_key)

    def load_wallet(self):
        self.wallet.load_keys()
        self.initialize_blockchain(self.wallet.public_key)

    def add_transaction(self):
        tx_recipient, tx_amount = self.get_transaction_info()
        signature = self.wallet.sign_transaction(self.wallet.public_key,
                                                 tx_recipient, tx_amount)
        if self.blockchain.add_transaction(tx_recipient,
                                           self.wallet.public_key,
                                           signature, tx_amount):
            print('Transaction added.')
        else:
            print('Transaction failed')
        print(self.blockchain.get_open_transactions())

    def listen_for_input(self):
        wait_for_input = True

        while wait_for_input:
            print('Please choose')
            print('1: Add a new transaction')
            print('2: Mine a new block')
            print('3: Output the blockchain')
            print('4: Check transactions validity')
            print('5: Create wallet')
            print('6: Load wallet')
            print('7: Save keys')
            print('q: Quit')
            user_choice = self.get_user_choice()
            if user_choice == '1':
                self.add_transaction()
            elif user_choice == '2':
                if not self.blockchain.mine_block():
                    print('Failed to mine new block. You do not have wallet.')
            elif user_choice == '3':
                self.print_blockchain()
            elif user_choice == '4':
                if Validator.verify_open_transactions(
                        self.blockchain.get_open_transactions(),
                        self.blockchain.get_balance):
                    print('All open transactions are valid.')
                else:
                    print('There is at least one invalid '
                          'transaction in open transactions.')
            elif user_choice == '5':
                self.create_wallet()
            elif user_choice == '6':
                self.load_wallet()
            elif user_choice == '7':
                self.wallet.save_keys_in_file()
            elif user_choice == 'q':
                wait_for_input = False
            else:
                print('Wrong choice!')

            if not Validator.verify_chain(self.blockchain.chain):
                print('Invalid blockchain!')
                wait_for_input = False

            self.print_balance()


if __name__ == '__main__':
    ui = Node()
    ui.listen_for_input()
