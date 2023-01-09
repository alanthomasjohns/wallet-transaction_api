from django.contrib import admin
from .models import Transaction, Wallet, PaymentRequest
# Register your models here.


admin.site.register(Wallet)
admin.site.register(PaymentRequest)
admin.site.register(Transaction)

# # create a custom Django Admin Model for the Transaction model
# class TransactionAdmin(admin.ModelAdmin):
#     # specify the fields to display in the list view
#     list_display = ['sender', 'receiver', 'amount', 'timestamp']

# # register the Transaction model with the Django Admin site
# admin.site.register(Transaction, TransactionAdmin)