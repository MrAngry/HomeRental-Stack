from django.contrib import admin
from django.urls import path

from payments.views import PaymentItemsView, ContractsView

urlpatterns = [
    path('payment_items/', PaymentItemsView.as_view()),
    path('contracts/', ContractsView.as_view()),
]
