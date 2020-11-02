from functools import wraps
from collections import OrderedDict
from hash_utils import hash_block, hash_string_sha256
import json
import os


class Blockchain():

    MINING_REWARD = 10
    OWNER = 'jaqb'
    GENESIS_BLOCK = {
        'previous_hash': '',
        'transactions': list(),
        'proof': 50
    }

    def __init__(self):
        self.blockchain = [self.GENESIS_BLOCK]
        self.open_transactions = list()
        self.participants = set([self.OWNER])
        if os.path.isfile('./blockchain.txt'):
            self.load_data()

    def print_wrapper(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            print('-' * 30)
            func(self, *args, **kwargs)
            print('-' * 30)
        return wrapper

    @print_wrapper
    def print_blockchain(self):
        for block in self.blockchain:
            print('Outputting block: ')
            print(block)

    @print_wrapper
    def output_participants(self):
        print('List of participants: ')
        for participant in self.participants:
            print(participant)

    def load_data(self):
        with open('blockchain.txt', 'r') as input_file:
            file_content = input_file.readlines()
            self.blockchain = json.loads(file_content[0].strip('\n'))
            self.blockchain = [{
                'previous_hash': block['previous_hash'],
                'proof': block['proof'],
                'transactions': [OrderedDict([
                    ('sender', tx['sender']),
                    ('recipient', tx['recipient']),
                    ('amount', tx['amount'])
                ]) for tx in block['transactions']]
            } for block in self.blockchain]
            self.open_transactions = json.loads(file_content[1].strip('\n'))
            self.open_transactions = [OrderedDict([
                ('sender', tx['sender']),
                ('recipient', tx['recipient']),
                ('amount', tx['amount'])
            ]) for tx in self.open_transactions]

    def save_data(self):
        with open('blockchain.txt', 'w') as output_file:
            output_file.write(json.dumps(self.blockchain))
            output_file.write('\n')
            output_file.write(json.dumps(self.open_transactions))

    def get_last_blockchain_item(self):
        if self.blockchain:
            return self.blockchain[-1]
        raise Exception('Empty blockchain!')

    def _get_balance(self, participant):
        tx_sender = [[tx['amount'] for tx in block['transactions']
                      if tx['sender'] == participant]
                     for block in self.blockchain]
        open_tx_sender = [tx['amount'] for tx in self.open_transactions
                          if tx['sender'] == participant]
        tx_sender.append(open_tx_sender)
        tx_recipient = [[tx['amount'] for tx in block['transactions']
                         if tx['recipient'] == participant]
                        for block in self.blockchain]

        sender_amount = sum([item for sublist in tx_sender
                             for item in sublist])
        recipient_amount = sum([item for sublist in tx_recipient
                                for item in sublist])
        return recipient_amount - sender_amount

    @print_wrapper
    def print_balance(self, participant):
        print('Balance of user {}: {:6.2f}'
              .format(participant, self._get_balance(participant)))

    def add_transaction(self, recipient, amount=1.0, sender=OWNER):
        new_transaction = OrderedDict([
            ('sender', sender),
            ('recipient', recipient),
            ('amount', amount)
        ])
        if self._verify_transaction(new_transaction):
            self.open_transactions.append(new_transaction)
            self.participants.add(sender)
            self.participants.add(recipient)
            self.save_data()
            return True
        return False

    def clear_open_transactions(self):
        self.open_transactions = list()

    def valid_proof(self, transactions, last_hash, proof):
        guess = (str(transactions) + str(last_hash) + str(proof)).encode()
        guess_hash = hash_string_sha256(guess)
        print(guess_hash)
        return guess_hash[0:2] == '00'

    def proof_of_work(self):
        last_block = self.get_last_blockchain_item()
        last_hash = hash_block(last_block)
        proof = 0
        while not self.valid_proof(self.open_transactions, last_hash, proof):
            proof += 1
        return proof

    def mine_block(self):
        last_block = self.get_last_blockchain_item()
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        reward_transaction = OrderedDict([
            ('sender', 'MINING'),
            ('recipient', self.OWNER),
            ('amount', self.MINING_REWARD)
        ])
        open_transactions_copy = self.open_transactions[:]
        open_transactions_copy.append(reward_transaction)
        block = {
            'previous_hash': hashed_block,
            'transactions': open_transactions_copy,
            'proof': proof
        }
        self.blockchain.append(block)
        self.clear_open_transactions()
        self.save_data()

    def verify_chain(self):
        for idx, block in enumerate(self.blockchain):
            if idx == 0:
                continue
            if block['previous_hash'] \
                    != hash_block(self.blockchain[idx - 1]):
                return False
            if not self.valid_proof(block['transactions'][:-1],
                                    block['previous_hash'], block['proof']):
                print('Proof of work is invalid.')
                return False
        return True

    def verify_open_transactions(self):
        return all([self._verify_transaction(tx)
                    for tx in self.open_transactions])

    def _verify_transaction(self, transaction):
        sender_balance = self._get_balance(transaction['sender'])
        return sender_balance >= transaction['amount']

    def get_transaction_info(self):
        tx_recipient = input('Enter the recipient of the transaction: ')
        tx_amount = float(input('Please pass transaction amount: '))
        return (tx_recipient, tx_amount)

    def get_user_choice(self):
        return input('Your choice: ')


bc = Blockchain()
wait_for_input = True

while wait_for_input:
    print('Please choose')
    print('1: Add a new transaction value')
    print('2: Mine a new block')
    print('3: Output the blockchain')
    print('4: Output participants')
    print('5: Check transactions validity')
    print('h: Manipulate the chain')
    print('q: Quit')
    user_choice = bc.get_user_choice()
    if user_choice == '1':
        tx_recipient, tx_amount = bc.get_transaction_info()
        if bc.add_transaction(tx_recipient, tx_amount):
            print('Transaction added.')
        else:
            print('Transaction failed.')
        print(bc.open_transactions)
    elif user_choice == '2':
        bc.mine_block()
    elif user_choice == '3':
        bc.print_blockchain()
    elif user_choice == '4':
        bc.output_participants()
    elif user_choice == '5':
        if bc.verify_open_transactions():
            print('All open transactions are valid.')
        else:
            print('There is at least one invalid '
                  'transaction in open transactions.')
    elif user_choice == 'h':
        if bc.blockchain:
            bc.blockchain[0] = {
                'previous_hash': '',
                'transactions': [{
                    'sender': 'Chris',
                    'recipient': 'Max',
                    'amount': 666.0
                }]
            }
    elif user_choice == 'q':
        wait_for_input = False
    else:
        print('Wrong choice!')

    if not bc.verify_chain():
        print('Invalid blockchain!')
        wait_for_input = False

    bc.print_balance('jaqb')
