from django.urls import path
from . import views

urlpatterns = [
    path('api/', views.get_ui, name='get-ui'),
    path('api/chain', views.get_chain, name='get-chain'),
    path('api/mine-block', views.mine, name='mine-block'),
    path('api/wallet', views.handle_keys, name='create-or-load-keys'),
    path('api/balance', views.get_balance, name='get-balance'),
    path('api/broadcast-transaction', views.broadcast_transaction, name='broadcast-transaction'),
    path('api/transaction', views.add_transaction, name='add-transaction'),
    path('api/transactions', views.get_open_transactions, name='get-open-transactions'),
    path('api/node', views.add_node, name='add-node'),
    path('api/node/<str:node_url>', views.remove_node, name='remove-node'),
    path('api/nodes', views.get_nodes, name='get-nodes')
]
