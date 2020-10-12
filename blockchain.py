
class blockchain():

    def __init__(self):
        self.blockchain = list()

    def print_blockchain(self):
        print('-' * 20)
        for block in self.blockchain:
            print('Outputting block: ')
            print(block)
        else:
            print('-' * 20)

    def get_last_blockchain_item(self):
        if self.blockchain:
            return self.blockchain[-1]
        raise Exception('Empty blockchain!')

    def add_transaction(self, transaction_amount, last_transaction=None):
        last_transaction = [
            1] if not self.blockchain else self.get_last_blockchain_item()

        self.blockchain.append(
            [last_transaction, transaction_amount])

    def verify_chain(self):
        for idx, block in enumerate(self.blockchain):
            if idx != 0 and block[0] != self.blockchain[idx - 1]:
                return False
        return True

    def get_transaction_amount(self):
        return float(input('Please pass transaction amount: '))

    def get_user_choice(self):
        return input('Your choice: ')


bc = blockchain()
wait_for_input = True

while wait_for_input:
    print('Please choose')
    print('1: Add a new transaction value')
    print('2: Output the blockchain')
    print('h: Manipulate the chain')
    print('q: Quit')
    user_choice = bc.get_user_choice()
    if user_choice == '1':
        tx_amount = bc.get_transaction_amount()
        bc.add_transaction(tx_amount)
    elif user_choice == '2':
        bc.print_blockchain()
    elif user_choice == 'h':
        if bc.blockchain:
            bc.blockchain[0] = [2]
    elif user_choice == 'q':
        wait_for_input = False
    else:
        print('Wrong choice!')

    if not bc.verify_chain():
        print('Invalid blockchain!')
        wait_for_input = False
