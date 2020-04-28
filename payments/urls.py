from django.contrib import admin
from django.urls import path

from payments.views import PaymentItemsView, ContractsView, SingleContractView, ContractPaymentItemsView

urlpatterns = [
    path('payment_items/', PaymentItemsView.as_view()),
    path('contracts/', ContractsView.as_view()),
    path('contracts/', ContractsView.as_view()),
    path('contracts/<int:id>/', SingleContractView.as_view()),
    path('contracts/<int:contract_id>/payment_items/', ContractPaymentItemsView.as_view()),
]
