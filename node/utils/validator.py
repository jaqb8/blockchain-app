from .hash_utils import hash_block, hash_string_sha256
from ..wallet import Wallet


class Validator:
    @classmethod
    def verify_chain(cls, blockchain):
        for idx, block in enumerate(blockchain):
            if idx == 0:
                continue
            if block.previous_hash \
                    != hash_block(blockchain[idx - 1]):
                return False
            if not cls.valid_proof(block.transactions[:-1],
                                   block.previous_hash, block.proof):
                print('Proof of work is invalid.')
                return False
        return True

    @classmethod
    def verify_open_transactions(cls, open_transactions, get_balance):
        return all([cls.verify_transaction(tx, get_balance, False)
                    for tx in open_transactions])

    @staticmethod
    def verify_transaction(transaction, get_balance, check_funds=True):
        if check_funds:
            sender_balance = get_balance(transaction.sender)
            return sender_balance >= transaction.amount and \
                Wallet.verify_transaction(transaction)
        else:
            return Wallet.verify_transaction(transaction)

    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        guess = (str([tx.to_ordered_dict() for tx in transactions])
                 + str(last_hash) + str(proof)).encode()
        guess_hash = hash_string_sha256(guess)
        return guess_hash[0:2] == '00'
