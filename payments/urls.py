from django.contrib import admin
from django.urls import path

from payments.views import PaymentItemsView

urlpatterns = [
    path('payment_items/', PaymentItemsView.as_view()),
]
