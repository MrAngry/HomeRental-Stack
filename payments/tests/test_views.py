from unittest import TestCase

from django.test import Client, TestCase

from payments.models import Contract, PaymentItem
from payments.serializers import PaymentItemSerializer, ContractSerializer


class TwoContractsMixin:
    def setUp(self):
        super().setUp()
        self.contract_1 = Contract.objects.create()
        list(PaymentItem.objects.create(value=x, contract=self.contract_1) for x in (100, 200, 300))

        self.contract_2 = Contract.objects.create()
        list(PaymentItem.objects.create(value=x, contract=self.contract_2) for x in (101, 202, 303))


class TestPaymentItemsView(TestCase):

    def test_get_payment_items_collection(self):
        contract = Contract.objects.create()
        payment_items = list(PaymentItem.objects.create(value=x, contract=contract) for x in (100, 200, 300))

        client = Client()
        response = client.get('/payments/payment_items/')
        self.assertEquals(200, response.status_code)

        self.assertSequenceEqual(response.json(), PaymentItemSerializer(instance=payment_items, many=True).data)


class TestContractsView(TwoContractsMixin, TestCase):
    def test_get(self):
        client = Client()
        response = client.get('/payments/contracts/')
        self.assertEquals(200, response.status_code)

        self.assertSequenceEqual(response.json(),
                                 ContractSerializer(instance=[self.contract_1, self.contract_2], many=True).data)


class TestSingleContractView(TwoContractsMixin, TestCase):
    def test_get(self):
        client = Client()
        response = client.get(f'/payments/contracts/{self.contract_2.id}/')

        self.assertDictEqual(response.json(), ContractSerializer(instance=self.contract_2).data)


class TestContractPaymentItemsView(TwoContractsMixin,TestCase):
    def test_post(self):
        client = Client()
        payment_item_json = {'value': '120.23', 'description': 'TEST_DESCRIPTION','contractId':self.contract_1.id}
        response = client.post(f'/payments/contracts/{self.contract_1.id}/payment_items/', data=payment_item_json,content_type='application/json')
        self.assertEquals(response.status_code,201)

        response = client.get(f'/payments/contracts/{self.contract_1.id}/')
        payment_items = response.json()['items']

        # Check if any `PaymentItem` returned in `response` has a subset of fields provided to POST method
        items_ = [set(payment_item_json.items()).issubset(set(p.items())) for p in payment_items]
        self.assertTrue(any(items_))

