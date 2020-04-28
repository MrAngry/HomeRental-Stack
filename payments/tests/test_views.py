from django.test import Client, TestCase

from payments.models import Contract, PaymentItem
from payments.serializers import PaymentItemSerializer


class TestPaymentItemsView(TestCase):
    def test_get_payment_items_collection(self):

        contract = Contract.objects.create()
        payment_items = list(PaymentItem.objects.create(value=x,contract=contract) for x in (100,200,300))

        client = Client()
        response = client.get('/payments/payment_items/')
        self.assertEquals(200, response.status_code)

        self.assertSequenceEqual(response.json(),PaymentItemSerializer(instance=payment_items,many=True).data)

