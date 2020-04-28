from rest_framework.serializers import ModelSerializer

from payments.models import PaymentItem


class PaymentItemSerializer(ModelSerializer):
    class Meta:
        model = PaymentItem
        fields = '__all__'
