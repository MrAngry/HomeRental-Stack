from rest_framework.serializers import ModelSerializer

from payments.models import PaymentItem, Contract


class PaymentItemSerializer(ModelSerializer):
    class Meta:
        model = PaymentItem
        fields = '__all__'


class ContractSerializer(ModelSerializer):
    items = PaymentItemSerializer(many=True)
    class Meta:
        model = Contract
        fields = '__all__'