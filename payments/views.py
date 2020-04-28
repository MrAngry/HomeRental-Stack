# Create your views here.
from rest_framework.parsers import JSONParser
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


class ContractPaymentItemsView(APIView):
    parser_classes = (JSONParser,)

    def post(self, request, contract_id):
        payload = request.data.copy()
        payload['contractId'] = contract_id  # Set/overwrite passed contractID in the body with one from URL

        payment_serializer = PaymentItemSerializer(data=payload)
        payment_serializer.is_valid(raise_exception=True)
        payment_serializer.save()
        return Response(status=201)


class ContractSinglePaymentItemView(APIView):
    parser_classes = (JSONParser,)

    def patch(self, request, contract_id, payment_item_id):
        payload = request.data.copy()
        payload['contractId'] = contract_id  # Set/overwrite passed contractID in the body with one from URL
        payload['id'] = payment_item_id  # Set/overwrite passed `PaymentItem` id in the body with one from URL

        payment_serializer = PaymentItemSerializer(
            instance=PaymentItem.objects.get(pk=payload['id'], contract_id=payload['contractId']),
            data=payload,
            partial=True)

        payment_serializer.is_valid(raise_exception=True)
        payment_serializer.save()
        return Response(status=202)

    def delete(self, request, contract_id, payment_item_id):
        try:
            payment_item = PaymentItem.objects.get(pk=payment_item_id,contract_id=contract_id)
            payment_item.delete()
            return Response(status=204)
        except PaymentItem.DoesNotExist:
            return Response(status=404)
