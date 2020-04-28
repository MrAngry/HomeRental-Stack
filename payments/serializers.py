from rest_framework.fields import IntegerField
from rest_framework.serializers import ModelSerializer

from payments.models import PaymentItem, Contract


class PaymentItemSerializer(ModelSerializer):
    contractId = IntegerField(source='contract.id')

    class Meta:
        model = PaymentItem
        exclude = ('contract',)

    # Changes to `create()` and `update()` are needed to support `contractId` as field name instead of `contract_id`
    # which is default for Django Rest Framework
    def create(self, validated_data):
        return Contract.objects.get(pk=validated_data['contract']['id']).items.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data['contract'] = Contract.objects.get(pk=validated_data['contract']['id'])
        return super().update(instance,validated_data)


class ContractSerializer(ModelSerializer):
    items = PaymentItemSerializer(many=True)

    class Meta:
        model = Contract
        fields = '__all__'
