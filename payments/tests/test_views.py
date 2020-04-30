from datetime import datetime, timedelta, date
from decimal import Decimal
from unittest import TestCase

import pytz
from django.test import Client, TestCase

from HomeRental_Stack import settings
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
        payment_item_json = {'value': '120.23', 'description': 'TEST_DESCRIPTION', 'contractId': self.contract_1.id,
                             'isDeleted': True, 'isImported': True}
        response = client.post(f'/payments/contracts/{self.contract_1.id}/payment_items/', data=payment_item_json,
                               content_type='application/json')
        self.assertEquals(response.status_code, 201)

        response = client.get(f'/payments/contracts/{self.contract_1.id}/')
        payment_items = response.json()['items']

        # Check if any `PaymentItem` returned in `response` has a subset of fields provided to POST method
        items_ = [set(payment_item_json.items()).issubset(set(p.items())) for p in payment_items]
        self.assertTrue(any(items_))

    def test_get_return_all_payment_items_for_contract(self):
        client = Client()

        response = client.get(f'/payments/contracts/{self.contract_1.id}/payment_items/')
        self.assertSequenceEqual(PaymentItemSerializer(instance=self.contract_1.items.all(), many=True).data,
                                 response.json()['items'])

    def test_get_returns_sum_of_all_payment_Values(self):
        client = Client()

        response = client.get(f'/payments/contracts/{self.contract_1.id}/payment_items/')
        self.assertEqual(sum(payment.value for payment in self.contract_1.items.all()), response.json()['sum'])

    def test_get_returns_payment_items_in_date_range(self):
        client = Client()
        contract = Contract.objects.create()
        payment_items = []

        test_dates = [datetime.now(tz=pytz.UTC) + timedelta(days=i) for i in range(-1, 2)]

        # Create test payments for yesterday, today and tomorrow
        for date in test_dates:
            payment_item = PaymentItem.objects.create(description="TEST DESCRIPTION", value=Decimal(100.23),
                                                      contract=contract)
            payment_item.createdAt = date
            payment_item.save(update_fields=['createdAt'])
            payment_items.append(payment_item)

        # Map datetime to string representation
        test_dates = [datetime.strftime(date, settings.REST_FRAMEWORK['DATETIME_FORMAT']) for date in test_dates]

        # Query for payments starting yesterday, today and tomorrow
        for index, date in enumerate(test_dates):
            response = client.get(f'/payments/contracts/{contract.id}/payment_items/',
                                  data={'startDate': date})
            expected = payment_items[index:]
            self.assertSequenceEqual(PaymentItemSerializer(instance=expected, many=True).data,
                                     response.json()['items'])

        # Query for payments created until tomorrow, today, yesterday
        for index, date in enumerate(test_dates):
            response = client.get(f'/payments/contracts/{contract.id}/payment_items/',
                                  data={'endDate': date})
            expected = payment_items[:-2 + index] if index - 2 else payment_items[:]
            self.assertSequenceEqual(PaymentItemSerializer(instance=expected, many=True).data,
                                     response.json()['items'])

        # Query for payments made today:
        response = client.get(f'/payments/contracts/{contract.id}/payment_items/',
                              data={'endDate': test_dates[1], 'startDate': test_dates[1]})
        expected = payment_items[1:2]
        self.assertSequenceEqual(PaymentItemSerializer(instance=expected, many=True).data,
                                 response.json()['items'])


class TestContractSinglePaymentItemView(TwoContractsMixin, TestCase):

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
        self.assertEquals(response.status_code, 204)

        # Check if any `PaymentItem` returned in `response` has a subset of fields provided to POST method
        self.contract_1.refresh_from_db()
        self.assertNotIn(first_payment_item, self.contract_1.items.all())

    def test_delete_404(self):
        client = Client()
        non_existent_id = PaymentItem.objects.last().pk + 1
        response = client.delete(f'/payments/contracts/{self.contract_1.id}/payment_items/{non_existent_id}/')
        self.assertEquals(response.status_code, 404)
