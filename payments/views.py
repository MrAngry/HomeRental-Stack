# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import PaymentItem
from payments.serializers import PaymentItemSerializer


class PaymentItemsView(APIView):
    def get(self, request):
        return Response(PaymentItemSerializer(PaymentItem.objects.all(), many=True).data,status=200)

