import functools


class blockchain():

    OWNER = 'jaqb'
    GENESIS_BLOCK = {
        'previous_hash': '',
        'transactions': list()
    }

    def __init__(self):
        self.blockchain = [self.GENESIS_BLOCK]
        self.open_transactions = list()
        self.participants = set([self.OWNER])

    def print_wrapper(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            print('-' * 20)
            func(self, *args, **kwargs)
            print('-' * 20)
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

    def get_last_blockchain_item(self):
        if self.blockchain:
            return self.blockchain[-1]
        raise Exception('Empty blockchain!')

    def _get_balance(self, participant):
        tx_sender = [[tx['amount'] for tx in block['transactions']
                      if tx['sender'] == participant]
                     for block in self.blockchain]
        tx_recipient = [[tx['amount'] for tx in block['transactions']
                         if tx['recipient'] == participant]
                        for block in self.blockchain]

        sender_amount = sum([amount[0] for amount in tx_sender if amount])
        recipient_amount = sum([amount[0]
                                for amount in tx_recipient if amount])
        return recipient_amount - sender_amount

    @print_wrapper
    def print_balance(self, participant):
        print(f'Balance of user {participant}:')
        print(self._get_balance(participant))

    def add_transaction(self, recipient, amount=1.0, sender=OWNER):
        new_transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        }
        self.open_transactions.append(new_transaction)
        self.participants.add(sender)
        self.participants.add(recipient)

    def clear_open_transactions(self):
        self.open_transactions = list()

    def hash_block(self, block):
        return '-'.join([str(value) for _, value in block.items()])

    def mine_block(self):
        last_block = self.get_last_blockchain_item()
        hashed_block = self.hash_block(last_block)
        block = {
            'previous_hash': hashed_block,
            'transactions': self.open_transactions
        }
        self.blockchain.append(block)
        self.clear_open_transactions()

    def verify_chain(self):
        for idx, block in enumerate(self.blockchain):
            if idx != 0 and block['previous_hash'] \
                    != self.hash_block(self.blockchain[idx - 1]):
                return False
        return True

    def get_transaction_info(self):
        tx_recipient = input('Enter the recipient of the transaction: ')
        tx_amount = float(input('Please pass transaction amount: '))
        return (tx_recipient, tx_amount)

    def get_user_choice(self):
        return input('Your choice: ')


bc = blockchain()
wait_for_input = True

while wait_for_input:
    print('Please choose')
    print('1: Add a new transaction value')
    print('2: Mine a new block')
    print('3: Output the blockchain')
    print('4: Output participants')
    print('h: Manipulate the chain')
    print('q: Quit')
    user_choice = bc.get_user_choice()
    if user_choice == '1':
        tx_recipient, tx_amount = bc.get_transaction_info()
        bc.add_transaction(tx_recipient, tx_amount)
        print(bc.open_transactions)
    elif user_choice == '2':
        bc.mine_block()
    elif user_choice == '3':
        bc.print_blockchain()
    elif user_choice == '4':
        bc.output_participants()
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
