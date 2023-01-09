from django.db import transaction
from django.db.models import Q
from users.models import User
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from .serializers import *
from .models import Wallet, Transaction, PaymentRequest
from rest_framework import status
from django.utils.decorators import decorator_from_middleware
from django.views.decorators.csrf import csrf_exempt

class WalletView(generics.UpdateAPIView):
    serializer_class = WalletSerializer

    def get_object(self):
        return self.request.user.wallet


class AddMoneyView(APIView):
    def get_object(self, user):
        try:
            return Wallet.objects.get(user=user)
        except Wallet.DoesNotExist:
            return Wallet(user=user)

    def post(self, request):
        wallet = self.get_object(request.user)
        serializer = WalletSerializer(wallet, data=request.data)
        if serializer.is_valid():
             # Add money to the user's wallet
            request.user.wallet.balance += serializer.validated_data['balance']
            request.user.wallet.save()
            # Update the user's balance
            request.user.balance += serializer.validated_data['balance']
            request.user.save()
            return Response({
                'status' : 200,
                'message' : 'successfuly added money to wallet',
                'data' : serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendPaymentView(APIView):

    @decorator_from_middleware(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        serializer = SendPaymentSerializer(data=request.data)
        if serializer.is_valid():
            # Get sender and receiver
            sender = request.user
            receiver_email = serializer.validated_data['receiver_email']
            try:
                receiver = User.objects.get(email=receiver_email)
            except User.DoesNotExist:
                return Response({'error': 'Receiver does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            # Check if sender has sufficient balance
            if sender.wallet.balance < serializer.validated_data['amount']:
                return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
            # Create and save transaction
            transaction = Transaction(sender=sender, receiver=receiver, amount=serializer.validated_data['amount'])
            transaction.save()
            # Update sender and receiver balances
            sender.wallet.balance -= serializer.validated_data['amount']
            sender.wallet.save()
            receiver.wallet.balance += serializer.validated_data['amount']
            receiver.wallet.save()
            sender.balance -= serializer.validated_data['amount']
            sender.save()
            receiver.balance += serializer.validated_data['amount']
            receiver.save()
            return Response({
                'status' : 200,
                'message' : f'Your money has been successfully sent to {receiver}',
                'data' : serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RequestPaymentView(APIView):
    @decorator_from_middleware(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        serializer = PaymentRequestSerializer(data=request.data)
        if serializer.is_valid():
            # Get sender and receiver
            sender = request.user
            receiver_email = serializer.validated_data['receiver']
            try:
                receiver = User.objects.get(email=receiver_email)
            except User.DoesNotExist:
                return Response({'error': 'Receiver does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create and save payment request
            payment_request = PaymentRequest(sender=sender, receiver=receiver, amount=serializer.validated_data['amount'])
            payment_request.save()
            return Response({"message":"Your payment request has been successfully sent to the user"},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AcceptRequestView(APIView):

    @decorator_from_middleware(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
        
    def post(self, request):
        serializer = AcceptRequestSerializer(data=request.data)
        if serializer.is_valid():
            # Get sender and receiver
            sender = request.user
            receiver_pk = serializer.validated_data['receiver']
            try:
                receiver = User.objects.get(pk=receiver_pk)
            except User.DoesNotExist:
                return Response({'error': 'Receiver does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            # Check if sender has sufficient balance
            if sender.wallet.balance < serializer.validated_data['amount']:
                return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
            # MultipleObjectsReturned
            try:
                payment_request = PaymentRequest.objects.get(sender=receiver, receiver=sender, amount=serializer.validated_data['amount'], status='pending')
            except PaymentRequest.MultipleObjectsReturned:
                return Response({'error': 'Multiple payment requests found. Please contact administrator.'}, status=status.HTTP_400_BAD_REQUEST)
            except PaymentRequest.DoesNotExist:
                return Response({'error': 'Payment request not found or already fulfilled'}, status=status.HTTP_400_BAD_REQUEST)
            # Update request status to fulfilled
            payment_request.status = 'fulfilled'
            payment_request.save()
            # Create and save transaction
            transaction = Transaction(sender=sender, receiver=receiver, amount=serializer.validated_data['amount'])
            transaction.save()
            # Update sender and receiver balances
            sender.wallet.balance -= serializer.validated_data['amount']
            sender.wallet.save()
            sender.balance -= serializer.validated_data['amount']
            sender.save()
            receiver.wallet.balance += serializer.validated_data['amount']
            receiver.wallet.save()
            receiver.balance += serializer.validated_data['amount']
            receiver.save()
            return Response({"message":"successfully send the requested amount to the user", "data" : serializer.data},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeclineRequestView(APIView):
    @decorator_from_middleware(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
        
    def post(self, request):
        serializer = DeclineRequestSerializer(data=request.data)
        if serializer.is_valid():
            # Get sender and receiver
            sender = request.user
            request_pk = serializer.validated_data['request']
            try:
                payment_request = PaymentRequest.objects.get(pk=request_pk)
            except PaymentRequest.DoesNotExist:
                return Response({'error': 'Payment request not found or already declined'}, status=status.HTTP_400_BAD_REQUEST)
            # Update request status to declined
            payment_request.status = 'declined'
            payment_request.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class TransactionHistoryView(APIView):
    def get(self, request):
        # Get all transactions involving the user as the sender or receiver
        transactions = Transaction.objects.filter(Q(sender=request.user) | Q(receiver=request.user))
        # Serialize the transactions and return them
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)