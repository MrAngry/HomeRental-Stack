from django.db import models

# Create your models here.
from django.db.models import Model, CharField, DecimalField, DateTimeField, ForeignKey, DO_NOTHING


class Contract(Model):

    def sum(self):
        return sum(payment.value for payment in self.items.all())


class Payment(Model):
    description = CharField(max_length=200, blank=True)
    value = DecimalField(max_digits=8,decimal_places=2, null=False)
    createdAt = DateTimeField(auto_now_add=True)
    updatedAt = DateTimeField(auto_now_add=True)
    contract = ForeignKey(to=Contract, on_delete=DO_NOTHING,related_name='items')
