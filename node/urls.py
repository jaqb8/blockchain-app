from django.urls import path
from . import views

urlpatterns = [
    path('api/', views.get_ui, name='get-ui'),
    path('api/chain', views.get_chain, name='get-chain')
]
