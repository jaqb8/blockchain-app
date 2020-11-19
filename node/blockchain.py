import json
from .utils.hash_utils import hash_block
from .block import Block
from .transaction import Transaction
from .utils.validator import Validator
from .wallet import Wallet
import requests


class Blockchain():

    MINING_REWARD = 10
    GENESIS_BLOCK = Block(index=0, previous_hash='',
                          proof=100, transactions=None,
                          timestamp=0)

    def __init__(self, public_key, node_id):
        self.chain = [self.GENESIS_BLOCK]
        self.__open_transactions = list()
        self.public_key = public_key
        self.__peer_nodes = set()
        self.node_id = str(node_id)
        self.resolve_confilcts = False
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
            with open(f'./node/blockchain-{self.node_id}', 'r') as input_file:
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
                self.__peer_nodes = set(json.loads(file_content[2].strip('\n')))
        except (IOError, IndexError):
            print('Blockchain file not found.')

    def save_data(self):
        try:
            with open(f'./node/blockchain-{self.node_id}', 'w') as output_file:
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
                output_file.write('\n')
                output_file.write(json.dumps(list(self.__peer_nodes)))
        except IOError:
            print('Saving failed!')

    def get_last_blockchain_item(self):
        if self.__chain:
            return self.__chain[-1]
        raise Exception('Empty blockchain!')

    def get_balance(self, sender=None):
        if sender is None:
            if self.public_key is None:
                raise Exception('Wallet is not set up.')
            participant = self.public_key
        else:
            participant = sender

        tx_sender = [[tx.amount for tx in block.transactions
                      if tx.sender == participant]
                     for block in self.__chain]
        open_tx_sender = [tx.amount for tx in self.__open_transactions
                          if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        tx_recipient = [[tx.amount for tx in block.transactions
                         if tx.recipient == participant]
                        for block in self.__chain]

        sender_amount = sum([item for sublist in tx_sender
                             for item in sublist])
        recipient_amount = sum([item for sublist in tx_recipient
                                for item in sublist])
        return recipient_amount - sender_amount

    def add_transaction(self, recipient, sender, signature, amount=1.0, is_receiving=False):
        if self.public_key is None:
            raise Exception('Wallet is not set up.')
        new_transaction = Transaction(sender, recipient, signature, amount)
        if Validator.verify_transaction(new_transaction,
                                        self.get_balance):
            self.__open_transactions.append(new_transaction)
            self.save_data()

            if not is_receiving:
                for node in self.__peer_nodes:
                    url = 'http://{}/api/broadcast-transaction'.format(node)
                    try:
                        response = requests.post(url, json={
                            'sender': sender,
                            'recipient': recipient,
                            'amount': amount,
                            'signature': signature
                        })
                        if response.status_code == 400 or response.status_code == 500:
                            print('Transaction declined, needs resolving')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        raise False

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
        if self.public_key is None:
            raise Exception('Wallet is not set up.')
        last_block = self.get_last_blockchain_item()
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        reward_transaction = Transaction('MINING', self.public_key,
                                         '', self.MINING_REWARD)
        open_transactions_copy = self.__open_transactions[:]
        for tx in open_transactions_copy:
            if not Wallet.verify_transaction(tx):
                raise Exception('Transactions are not valid.')
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
        for node in self.__peer_nodes:
            url = 'http://{}/api/broadcast-block'.format(node)
            dict_block = block.__dict__.copy()
            dict_block['transactions'] = [tx.__dict__
                                          for tx in dict_block['transactions']]
            try:
                response = requests.post(url, json={
                    'block': dict_block
                })
                if response.status_code == 400 or response.status_code == 500:
                    print('Block declined, needs resolving')
                if response.status_code == 409:
                    self.resolve_confilcts = True
            except requests.exceptions.ConnectionError:
                continue
        return block

    def add_block(self, block):
        transactions = [Transaction(tx['sender'],
                                    tx['recipient'],
                                    tx['signature'],
                                    tx['amount']) for tx in block['transactions']]
        proof_is_valid = Validator.valid_proof(transactions[:-1],
                                               block['previous_hash'],
                                               block['proof'])
        hashes_match = hash_block(self.chain[-1]) == block['previous_hash']
        if not proof_is_valid or not hashes_match:
            return False
        block_object = Block(block['index'],
                             block['previous_hash'],
                             block['proof'],
                             transactions,
                             block['timestamp'])
        self.__chain.append(block_object)
        stored_transactions = self.__open_transactions[:]
        for incoming_tx in block['transactions']:
            for open_tx in stored_transactions:
                if open_tx.sender == incoming_tx['sender'] \
                        and open_tx.recipient == incoming_tx['recipient'] \
                        and open_tx.signature == incoming_tx['signature'] \
                        and open_tx.amount == incoming_tx['amount']:
                    try:
                        self.__open_transactions.remove(open_tx)
                    except ValueError:
                        print('Item was already removed.')
        self.save_data()
        return True

    @staticmethod
    def parse_chain_to_objects(chain):
        parsed_chain = [Block(block['index'],
                              block['previous_hash'],
                              block['proof'],
                              [Transaction(tx['sender'],
                                           tx['recipient'],
                                           tx['signature'],
                                           tx['amount'])
                               for tx in block['transactions']],
                              block['timestamp']) for block in chain]
        return parsed_chain

    def resolve(self):
        winner_chain = self.chain
        is_chain_replaced = False
        for node in self.__peer_nodes:
            url = 'http://{}/api/chain'.format(node)
            try:
                response = requests.get(url)
                node_chain = response.json()
                node_chain = self.parse_chain_to_objects(node_chain)
                if len(node_chain) > len(winner_chain) \
                        and Validator.verify_chain(node_chain):
                    winner_chain = node_chain
                    is_chain_replaced = True
            except requests.exceptions.ConnectionError:
                continue
        self.resolve_confilcts = False
        self.chain = winner_chain
        if is_chain_replaced:
            self.clear_open_transactions()
        self.save_data()
        return is_chain_replaced

    def add_peer_node(self, node_url):
        self.__peer_nodes.add(node_url)
        self.save_data()

    def remove_peer_node(self, node_url):
        self.__peer_nodes.discard(node_url)
        self.save_data()

    def get_peer_nodes(self):
        return list(self.__peer_nodes)
