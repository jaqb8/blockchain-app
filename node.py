from functools import wraps
from blockchain import Blockchain
from uuid import uuid4
from validator import Validator


class Node:
    def __init__(self):
        self.node_id = str(uuid4())
        self.blockchain = Blockchain(self.node_id)

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
              .format(self.node_id, self.blockchain.get_balance()))

    def get_transaction_info(self):
        tx_recipient = input('Enter the recipient of the transaction: ')
        tx_amount = float(input('Please pass transaction amount: '))
        return (tx_recipient, tx_amount)

    def get_user_choice(self):
        return input('Your choice: ')

    def listen_for_input(self):
        wait_for_input = True

        while wait_for_input:
            print('Please choose')
            print('1: Add a new transaction value')
            print('2: Mine a new block')
            print('3: Output the blockchain')
            print('4: Check transactions validity')
            print('q: Quit')
            user_choice = self.get_user_choice()
            if user_choice == '1':
                tx_recipient, tx_amount = self.get_transaction_info()
                if self.blockchain.add_transaction(tx_recipient,
                                                   self.node_id, tx_amount):
                    print('Transaction added.')
                else:
                    print('Transaction failed.')
                print(self.blockchain.get_open_transactions())
            elif user_choice == '2':
                self.blockchain.mine_block()
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
            elif user_choice == 'q':
                wait_for_input = False
            else:
                print('Wrong choice!')

            if not Validator.verify_chain(self.blockchain.chain):
                print('Invalid blockchain!')
                wait_for_input = False

            self.print_balance()


ui = Node()
ui.listen_for_input()
