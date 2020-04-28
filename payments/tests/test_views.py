from decimal import Decimal
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


class TestContractPaymentItemsView(TwoContractsMixin, TestCase):
    def test_post(self):
        client = Client()
        payment_item_json = {'value': '120.23', 'description': 'TEST_DESCRIPTION', 'contractId': self.contract_1.id}
        response = client.post(f'/payments/contracts/{self.contract_1.id}/payment_items/', data=payment_item_json,
                               content_type='application/json')
        self.assertEquals(response.status_code, 201)

        response = client.get(f'/payments/contracts/{self.contract_1.id}/')
        payment_items = response.json()['items']

        # Check if any `PaymentItem` returned in `response` has a subset of fields provided to POST method
        items_ = [set(payment_item_json.items()).issubset(set(p.items())) for p in payment_items]
        self.assertTrue(any(items_))

    def test_patch(self):
        client = Client()
        first_payment_item = self.contract_1.items.first()
        payment_item_id = first_payment_item.id
        payment_item_json = {'value': '120.23', 'description': 'TEST_DESCRIPTION', 'contractId': self.contract_1.id,
                             'id': payment_item_id}
        response = client.patch(f'/payments/contracts/{self.contract_1.id}/payment_items/{payment_item_id}/',
                                data=payment_item_json,
                                content_type='application/json')

        self.assertEquals(response.status_code, 202)
        first_payment_item = self.contract_1.items.first()
        self.assertEquals(first_payment_item.value, Decimal(payment_item_json['value']))
        self.assertEquals(first_payment_item.description, payment_item_json['description'])

    def test_delete(self):
        client = Client()
        first_payment_item = self.contract_1.items.first()
        self.assertIn(first_payment_item, self.contract_1.items.all())

        response = client.delete(f'/payments/contracts/{self.contract_1.id}/payment_items/{first_payment_item.id}/')
        self.assertEquals(response.status_code,204)

        # Check if any `PaymentItem` returned in `response` has a subset of fields provided to POST method
        self.contract_1.refresh_from_db()
        self.assertNotIn(first_payment_item,self.contract_1.items.all())

    def test_delete_404(self):
        client = Client()
        non_existent_id = PaymentItem.objects.last().pk + 1
        response = client.delete(f'/payments/contracts/{self.contract_1.id}/payment_items/{non_existent_id}/')
        self.assertEquals(response.status_code,404)
