from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .blockchain import Blockchain
from .wallet import Wallet

wallet = Wallet
blockchain = Blockchain(wallet.public_key)


@api_view()
def get_ui(request):
    return Response({'msg': 'It works!'})


@api_view()
def get_chain(request):
    chain = blockchain.chain
    json_chain = [block.__dict__.copy() for block in chain]
    for block in json_chain:
        block['transactions'] = [tx.__dict__ for tx in block['transactions']]
    return Response(json_chain)
