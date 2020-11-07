import hashlib
import json


def hash_string_sha256(string):
    return hashlib.sha256(string).hexdigest()


def hash_block(block):
    block_as_dict = block.__dict__.copy()
    block_as_dict['transactions'] = [tx.to_ordered_dict()
                                     for tx in block_as_dict['transactions']]
    return hash_string_sha256(json.dumps(block_as_dict, sort_keys=True)
                              .encode())
