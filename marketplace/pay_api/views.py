from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import PaymentSerializer
import time


class PaymentsAPIView(APIView):

    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order_number = serializer.validated_data['order_number']
        bank_card = serializer.validated_data['bank_card']
        time.sleep(10)
        if (int(bank_card) % 2 == 0) and bank_card[-1:] != '0':
            return Response({'order_number': order_number, 'status': 'paid'},
                            status=200)
        else:
            return Response({'order_number': order_number, 'status': 'error'},
                            status=400)
