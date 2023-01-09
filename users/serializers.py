from rest_framework import serializers
from .models import User
from wallet.models import Wallet
from wallet.serializers import WalletSerializer
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
# from account.utils import Util

class UserRegistrationSerializer(serializers.ModelSerializer):

  wallet = WalletSerializer(required=False, default={'balance': 0.0})
  class Meta:
        model = User
        fields = ['name', 'email', 'date_joined','password', 'is_active','balance', 'wallet', 'is_banned']

        extra_kwargs = {
            'password' : {'write_only' : True}
        }

  def create(self, validated_data):
      wallet_data = validated_data.pop('wallet')
      user = User.objects.create(**validated_data)
      Wallet.objects.create(user=user, **wallet_data)
      password=self.validated_data['password']
      user.set_password(password)
      user.save()
      return user


class UserLoginSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(max_length=255)
  class Meta:
    model = User
    fields = ['email', 'password']

class UserProfileSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id', 'email', 'name','is_banned']

class UserChangePasswordSerializer(serializers.Serializer):
  password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  password2 = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  class Meta:
    fields = ['password', 'password2']

  def validate(self, attrs):
    password = attrs.get('password')
    password2 = attrs.get('password2')

    user = self.context.get('user')

    if user.check_password(password):
      user.set_password(password2)
      user.save()

    else:
      raise serializers.ValidationError("Password wrong")
    return attrs

