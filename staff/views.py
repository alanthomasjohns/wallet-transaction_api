from django.shortcuts import render
from rest_framework import generics, filters
from rest_framework.filters import SearchFilter, OrderingFilter
from users.models import User
from .serializers import UserSerializer, BanUserSerializer, UnbanUserSerializer
from wallet.models import Transaction
from django.db.models import Q
from wallet.serializers import TransactionSerializer
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


# Create your views here.


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class UserTransactionsAPIView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        user = self.kwargs['user']
        return Transaction.objects.filter(Q(sender=user) | Q(receiver=user))


class TransactionListAPIView(ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    permission_classes = [IsAdminUser]
    search_fields = ['sender__email', 'receiver__email']
    ordering_fields = ['transaction_date']


class TransactionDetailAPIView(generics.RetrieveAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAdminUser]


class BanUserView(APIView):

    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = BanUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UnbanUserView(APIView):
    def post(self, request):
        serializer = UnbanUserSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            user.is_active = True
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
