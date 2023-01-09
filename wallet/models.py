from django.db import models
from users.models import User

# Create your models here.


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

class Transaction(models.Model):
    sender = models.ForeignKey(User, related_name='sender', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='receiver', on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)


class PaymentRequest(models.Model):
    sender = models.ForeignKey(User, related_name='sent_payment_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_payment_requests', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('fulfilled', 'Fulfilled'), ('declined', 'Declined')], default='pending')


