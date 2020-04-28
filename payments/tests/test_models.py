import random
from decimal import Decimal

from django.test import TestCase

from payments.models import Contract, PaymentItem


class TestContract(TestCase):
    def test_sum(self):
        # Generate random payments value
        values = list(Decimal(random.randrange(0, 100)) / 100 + Decimal(random.randrange(0, 2000)) for i in range(30))

        contract = Contract.objects.create()
        payments = list(PaymentItem.objects.create(value=value, contract=contract) for value in values)

        self.assertEquals(sum(values), contract.sum(),msg="Summing method failed")
