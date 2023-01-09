from rest_framework import serializers
from wallet.models import Transaction
from wallet.serializers import TransactionSerializer
from users.models import User
from django.db.models import Q
from rest_framework import generics

class UserSerializer(serializers.ModelSerializer):
    transactions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'date_joined', 'is_active', 'balance', 'transactions']
        read_only_fields = ['id', 'date_joined', 'is_active', 'balance']

    def get_transactions(self, obj):
        transactions = Transaction.objects.filter(Q(sender=obj) | Q(receiver=obj))
        return TransactionSerializer(transactions, many=True).data



class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'sender', 'receiver', 'amount']


class BanUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['is_banned']


class UnbanUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()


