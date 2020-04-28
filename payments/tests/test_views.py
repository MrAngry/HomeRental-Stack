from unittest import TestCase

from django.test import Client, TestCase

from payments.models import Contract, PaymentItem
from payments.serializers import PaymentItemSerializer, ContractSerializer


class TestPaymentItemsView(TestCase):
    def test_get_payment_items_collection(self):
        contract = Contract.objects.create()
        payment_items = list(PaymentItem.objects.create(value=x, contract=contract) for x in (100, 200, 300))

        client = Client()
        response = client.get('/payments/payment_items/')
        self.assertEquals(200, response.status_code)

        self.assertSequenceEqual(response.json(), PaymentItemSerializer(instance=payment_items, many=True).data)


class TestContractsView(TestCase):
    def test_get(self):
        contract_1 = Contract.objects.create()
        payment_items = list(PaymentItem.objects.create(value=x, contract=contract_1) for x in (100, 200, 300))

        contract_2 = Contract.objects.create()
        payment_items = list(PaymentItem.objects.create(value=x, contract=contract_1) for x in (100, 200, 300))

        client = Client()
        response = client.get('/payments/contracts/')
        self.assertEquals(200, response.status_code)

        self.assertSequenceEqual(response.json(), ContractSerializer(instance=[contract_1,contract_2],many=True).data)




