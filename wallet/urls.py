from django.urls import path
from django.db.models import Q
from . import views

urlpatterns = [
    path('send-payment/', views.SendPaymentView.as_view(), name='send-payment'),
    path('request-payment/', views.RequestPaymentView.as_view(), name='request-payment'),
    path('accept-request/', views.AcceptRequestView.as_view(), name='accept-request'),
    path('decline-request/', views.DeclineRequestView.as_view(), name='decline-request'),
    path('wallet/', views.WalletView.as_view(), name='wallet'),
    path('add-money/', views.AddMoneyView.as_view(), name='add-money'),
    path('view-transactions/', views.TransactionHistoryView.as_view(), name='view-transactions'),
]