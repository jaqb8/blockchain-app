import json
from utils.hash_utils import hash_block
from block import Block
from transaction import Transaction
from utils.validator import Validator
from wallet import Wallet


class Blockchain():

    MINING_REWARD = 10
    GENESIS_BLOCK = Block(index=0, previous_hash='',
                          proof=100, transactions=None,
                          timestamp=0)

    def __init__(self, hosting_node):
        self.chain = [self.GENESIS_BLOCK]
        self.__open_transactions = list()
        self.hosting_node = hosting_node
        self.load_data()

    @property
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, value):
        self.__chain = value

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def load_data(self):
        try:
            with open('blockchain.txt', 'r') as input_file:
                file_content = input_file.readlines()
                blockchain = json.loads(file_content[0].strip('\n'))
                self.chain = [Block(
                    index=block['index'],
                    previous_hash=block['previous_hash'],
                    proof=block['proof'],
                    transactions=[Transaction(
                        sender=tx['sender'],
                        recipient=tx['recipient'],
                        signature=tx['signature'],
                        amount=tx['amount']
                    ) for tx in block['transactions']],
                    timestamp=block['timestamp']
                ) for block in blockchain]
                open_transactions = json \
                    .loads(file_content[1].strip('\n'))
                self.__open_transactions = [Transaction(
                    sender=tx['sender'],
                    recipient=tx['recipient'],
                    signature=tx['signature'],
                    amount=tx['amount']
                ) for tx in open_transactions]
        except (IOError, IndexError):
            print('Blockchain file not found.')

    def save_data(self):
        try:
            with open('blockchain.txt', 'w') as output_file:
                parsed_chain = [block.__dict__
                                for block in [
                                    Block(
                                        block_element.index,
                                        block_element.previous_hash,
                                        block_element.proof,
                                        [tx.__dict__ for
                                         tx in block_element.transactions],
                                        block_element.timestamp
                                    ) for block_element in self.__chain
                                ]]
                output_file.write(json.dumps(parsed_chain))
                output_file.write('\n')
                parsed_tx = [tx.__dict__ for tx in self.__open_transactions]
                output_file.write(json.dumps(parsed_tx))
        except IOError:
            print('Saving failed!')

    def get_last_blockchain_item(self):
        if self.__chain:
            return self.__chain[-1]
        raise Exception('Empty blockchain!')

    def get_balance(self):
        tx_sender = [[tx.amount for tx in block.transactions
                      if tx.sender == self.hosting_node]
                     for block in self.__chain]
        open_tx_sender = [tx.amount for tx in self.__open_transactions
                          if tx.sender == self.hosting_node]
        tx_sender.append(open_tx_sender)
        tx_recipient = [[tx.amount for tx in block.transactions
                         if tx.recipient == self.hosting_node]
                        for block in self.__chain]

        sender_amount = sum([item for sublist in tx_sender
                             for item in sublist])
        recipient_amount = sum([item for sublist in tx_recipient
                                for item in sublist])
        return recipient_amount - sender_amount

    def add_transaction(self, recipient, sender, signature, amount=1.0):
        if self.hosting_node is None:
            return False
        new_transaction = Transaction(sender, recipient, signature, amount)
        if Validator.verify_transaction(new_transaction,
                                        self.get_balance):
            self.__open_transactions.append(new_transaction)
            self.save_data()
            return True
        return False

    def clear_open_transactions(self):
        self.__open_transactions = list()

    def proof_of_work(self):
        last_block = self.get_last_blockchain_item()
        last_hash = hash_block(last_block)
        proof = 0
        while not Validator.valid_proof(self.__open_transactions,
                                        last_hash, proof):
            proof += 1
        return proof

    def mine_block(self):
        if self.hosting_node is None:
            return False
        last_block = self.get_last_blockchain_item()
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        reward_transaction = Transaction('MINING', self.hosting_node,
                                         '', self.MINING_REWARD)
        open_transactions_copy = self.__open_transactions[:]
        for tx in open_transactions_copy:
            if not Wallet.verify_transaction(tx):
                return False
        open_transactions_copy.append(reward_transaction)
        block = Block(
            index=len(self.__chain),
            previous_hash=hashed_block,
            proof=proof,
            transactions=open_transactions_copy,
        )
        self.__chain.append(block)
        self.clear_open_transactions()
        self.save_data()
        return True
