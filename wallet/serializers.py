from rest_framework import serializers, generics
from .models import Wallet, Transaction, PaymentRequest
from users.models import User


class WalletSerializer(serializers.ModelSerializer):

    balance = serializers.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        model = Wallet
        fields = ['balance']
        read_only_fields = ['user']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['balance'] = instance.balance
        return data
    
    def update(self, instance, validated_data):
        instance.balance += validated_data.get('amount', 0)
        instance.save()
        return instance



class SendPaymentSerializer(serializers.ModelSerializer):
    receiver_email = serializers.EmailField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)

    class Meta:
        model = Transaction
        fields = ['receiver_email', 'amount','balance']
        read_only_fields = ['sender']



class PaymentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentRequest
        fields = ['sender', 'receiver', 'amount', 'status']
        read_only_fields = ['sender', 'created_at']



class TransactionSerializer(serializers.ModelSerializer):
    sender = WalletSerializer(read_only=True)
    recipient = WalletSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = ('id', 'sender', 'recipient', 'amount', 'transaction_date')
        read_only_fields = ('sender', 'recipient', 'amount', 'transaction_date')



class AcceptRequestSerializer(serializers.Serializer):
    receiver = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    
    def validate_receiver(self, value):
        try:
            User.objects.get(pk=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('Receiver does not exist')
        return value


class DeclineRequestSerializer(serializers.Serializer):
    request = serializers.IntegerField()
    
    def validate(self, data):
        try:
            payment_request = PaymentRequest.objects.get(pk=data['request'])
        except PaymentRequest.DoesNotExist:
            raise serializers.ValidationError({'request': 'Invalid payment request'})
        
        if payment_request.receiver != self.context['request'].user:
            raise serializers.ValidationError({'request': 'You are not authorized to decline this request'})
        
        if payment_request.status != 'pending':
            raise serializers.ValidationError({'request': 'Cannot decline a request that is not pending'})
        
        return data


