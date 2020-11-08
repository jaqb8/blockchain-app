from Crypto.PublicKey import RSA
import Crypto.Random
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import binascii


class Wallet:
    def __init__(self):
        self.private_key = None
        self.public_key = None

    @property
    def public_key(self):
        return self.__public_key

    @public_key.setter
    def public_key(self, value):
        self.__public_key = value

    def save_keys_in_file(self):
        if self.private_key is not None and self.public_key is not None:
            try:
                with open('wallet.txt', mode='w') as output_file:
                    output_file.write(self.private_key)
                    output_file.write('\n')
                    output_file.write(self.public_key)
            except (IOError, IndexError):
                print('Saving wallet failed.')

    def create_keys(self):
        private_key, public_key = self.generate_keys()
        self.private_key = private_key
        self.public_key = public_key

    def load_keys(self):
        try:
            with open('wallet.txt', mode='r') as input_file:
                file_content = input_file.readlines()
                self.private_key = file_content[0].strip('\n')
                self.public_key = file_content[1]
        except IOError:
            print('Loading wallet failed.')

    def generate_keys(self):
        private_key = RSA.generate(2048, Crypto.Random.new().read)
        public_key = private_key.publickey()
        return (binascii.hexlify(private_key
                                 .exportKey(format='DER')).decode('ascii'),
                binascii.hexlify(public_key
                                 .exportKey(format='DER')).decode('ascii'))

    def sign_transaction(self, sender, recipient, amount):
        signer = PKCS1_v1_5.new(RSA.importKey(binascii
                                              .unhexlify(self.private_key)))
        payload_hash = SHA256.new((str(sender) + str(recipient) + str(amount))
                                  .encode('utf8'))
        signature = signer.sign(payload_hash)
        return binascii.hexlify(signature).decode('ascii')

    @staticmethod
    def verify_transaction(transaction):
        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        payload_hash = SHA256.new((str(transaction.sender)
                                   + str(transaction.recipient)
                                   + str(transaction.amount))
                                  .encode('utf8'))
        return verifier.verify(payload_hash,
                               binascii.unhexlify(transaction.signature))
