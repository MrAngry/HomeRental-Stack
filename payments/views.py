# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import PaymentItem, Contract
from payments.serializers import PaymentItemSerializer, ContractSerializer


class PaymentItemsView(APIView):
    def get(self, request):
        return Response(PaymentItemSerializer(PaymentItem.objects.all(), many=True).data, status=200)


class ContractsView(APIView):
    def get(self, request):
        return Response(ContractSerializer(Contract.objects.all(), many=True).data, status=200)


class SingleContractView(APIView):
    def get(self, request, id):
        return Response(ContractSerializer(Contract.objects.get(pk=id), many=False).data, status=200)
