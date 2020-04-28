from rest_framework.fields import IntegerField
from rest_framework.serializers import ModelSerializer

from payments.models import PaymentItem, Contract


class PaymentItemSerializer(ModelSerializer):
    contractId = IntegerField(source='contract.id')

    class Meta:
        model = PaymentItem
        exclude = ('contract',)

    def create(self, validated_data):
        return Contract.objects.get(pk=validated_data['contract']['id']).items.create(**validated_data)


class ContractSerializer(ModelSerializer):
    items = PaymentItemSerializer(many=True)

    class Meta:
        model = Contract
        fields = '__all__'
