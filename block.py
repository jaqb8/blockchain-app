from time import time
from utils.printable import Printable


class Block(Printable):
    def __init__(self, index, previous_hash,
                 proof, transactions, timestamp=None):
        self.index = index
        self.previous_hash = previous_hash
        self.proof = proof
        self.transactions = transactions \
            if transactions is not None else list()
        self.timestamp = timestamp if timestamp is not None else time()
