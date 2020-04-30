# Create your views here.
import datetime

from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from HomeRental_Stack import settings
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

    def get(self, request, contract_id):
        try:
            payment_items = Contract.objects.get(pk=contract_id).items.all()
            ple = list(payment_items)
            if request.GET.get('startDate'):
                target_start_date = datetime.datetime.strptime(request.GET['startDate'],
                                                               settings.REST_FRAMEWORK['DATETIME_FORMAT'])
                payment_items = payment_items.filter(createdAt__gte=target_start_date)
            if request.GET.get('endDate'):
                target_end_date = datetime.datetime.strptime(request.GET['endDate'],
                                                             settings.REST_FRAMEWORK['DATETIME_FORMAT'])
                payment_items = payment_items.filter(createdAt__lte=target_end_date)

            return Response(status=200, data=PaymentItemSerializer(instance=payment_items, many=True).data)
        except Contract.DoesNotExist:
            return Response(status=404, data=f"No contract with ID:{contract_id}")


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
            payment_item = PaymentItem.objects.get(pk=payment_item_id, contract_id=contract_id)
            payment_item.delete()
            return Response(status=204)
        except PaymentItem.DoesNotExist:
            return Response(status=404)
