from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .blockchain import Blockchain
from .wallet import Wallet
import os

port = os.environ['DJANGO_APP_PORT']
print(port)
wallet = Wallet(port)
blockchain = Blockchain(wallet.public_key, port)


@api_view()
def get_ui(request):
    return Response({'msg': 'It works!'})


@api_view(['GET', 'POST'])
def handle_keys(request):
    try:
        if request.method == 'POST':
            wallet.create_keys()
            wallet.save_keys_in_file()
        elif request.method == 'GET':
            wallet.load_keys()
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        return Response({
            'private_key': wallet.private_key,
            'public_key': wallet.public_key,
            'balance': blockchain.get_balance()
        })
    except Exception as err_msg:
        return Response({
            'msg': str(err_msg)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view()
def get_balance(request):
    try:
        balance = blockchain.get_balance()
        return Response({
            'msg': 'Fetched balance successfully.',
            'balance': balance
        })
    except Exception as err_msg:
        return Response({
            'msg': str(err_msg),
            'wallet_set_up': wallet.public_key is not None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def add_transaction(request):
    request_body = request.data
    required_fields = ['recipient', 'amount']
    if not all(field in request_body for field in required_fields):
        return Response({
            'msg': 'Required data is missing.'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        signature = wallet.sign_transaction(wallet.public_key,
                                            request_body['recipient'],
                                            request_body['amount'])
        blockchain.add_transaction(request_body['recipient'],
                                   wallet.public_key,
                                   signature,
                                   request_body['amount'])
        return Response({
            'msg': 'Transaction added successfully.',
            'transaction': {
                'sender': wallet.public_key,
                'recipient': request_body['recipient'],
                'signature': signature,
                'amount': request_body['amount']
            },
            'balance': blockchain.get_balance()
        }, status=status.HTTP_201_CREATED)
    except Exception as err_msg:
        return Response({
            'msg': str(err_msg)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def broadcast_transaction(request):
    request_body = request.data
    required_fields = ['sender', 'recipient', 'amount', 'signature']
    if not request_body or not all(field in request_body for field in required_fields):
        return Response({
            'msg': 'Required data is missing.'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        blockchain.add_transaction(request_body['recipient'],
                                   request_body['sender'],
                                   request_body['signature'],
                                   request_body['amount'],
                                   is_receiving=True)
        return Response({
            'msg': 'Transaction added successfully.',
            'transaction': {
                'sender': request_body['sender'],
                'recipient': request_body['recipient'],
                'signature': request_body['signature'],
                'amount': request_body['amount']
            }
        }, status=status.HTTP_201_CREATED)
    except Exception as err_msg:
        return Response({
            'msg': str(err_msg)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def mine(request):
    try:
        block = blockchain.mine_block()
        json_block = block.__dict__.copy()
        json_block['transactions'] = [tx.__dict__ for tx
                                      in json_block['transactions']]
        return Response({
            'msg': 'Block added successfully.',
            'block': json_block,
            'balance': blockchain.get_balance()
        })
    except Exception as err_msg:
        return Response({
            'msg': str(err_msg),
            'wallet_set_up': wallet.public_key is not None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view()
def get_open_transactions(request):
    try:
        open_transactions = blockchain.get_open_transactions()
        json_transactions = [tx.__dict__ for tx in open_transactions]
        return Response(json_transactions)
    except Exception as err_msg:
        return Response({
            'msg': str(err_msg)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view()
def get_chain(request):
    chain = blockchain.chain
    json_chain = [block.__dict__.copy() for block in chain]
    for block in json_chain:
        block['transactions'] = [tx.__dict__ for tx in block['transactions']]
    return Response(json_chain)


@api_view(['POST'])
def add_node(request):
    request_body = request.data
    if not request_body or 'node' not in request_body:
        return Response({
            'msg': 'Required data is missing.'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        blockchain.add_peer_node(request_body['node'])
        return Response({
            'msg': 'Node added.',
            'all_nodes': blockchain.get_peer_nodes()
        }, status=status.HTTP_201_CREATED)
    except Exception as err_msg:
        return Response({
            'msg': str(err_msg)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def remove_node(request, node_url):
    try:
        blockchain.remove_peer_node(node_url)
        return Response({
            'msg': 'Node removed.',
            'all_nodes': blockchain.get_peer_nodes()
        })
    except Exception as err_msg:
        return Response({
            'msg': str(err_msg)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view()
def get_nodes(request):
    try:
        return Response({
            'all_nodes': blockchain.get_peer_nodes()
        })
    except Exception as err_msg:
        return Response({
            'msg': str(err_msg)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
