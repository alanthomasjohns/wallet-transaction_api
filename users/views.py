from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from wallet.models import Wallet
from rest_framework.views import APIView
from .serializers import UserChangePasswordSerializer, UserLoginSerializer, UserProfileSerializer, UserRegistrationSerializer
from django.contrib.auth import authenticate
from .renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import logout
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication

# Generate Token Manually
def get_tokens_for_user(user):
  refresh = RefreshToken.for_user(user)
  return {
      'refresh': str(refresh),
      'access': str(refresh.access_token),
  }


class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data.get('email')
    password = serializer.data.get('password')
    user = authenticate(email=email, password=password)
    if user is not None:
      token = get_tokens_for_user(user)
      return Response({'token':token, 'msg':'Login Success'}, status=status.HTTP_200_OK)
    else:
      return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)


class UserProfileView(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated]
  def get(self, request, format=None):
    print("*******************************")
    print(request.user)
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)

class UserChangePasswordView(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated]
  def post(self, request, format=None):
    serializer = UserChangePasswordSerializer(data=request.data, context={'user':request.user})
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Changed Successfully'}, status=status.HTTP_200_OK)



class UserDetails(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except:
            return Http404

    def get(self, request, pk, format=None):
        userData=self.get_object(pk)
        serializer = UserProfileSerializer(userData)
        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        user = request.user
        print(user)
        userData = self.get_object(pk)
        print(userData)

        if user == userData:
          serializer = UserProfileSerializer(userData, data=request.data, partial=True)
          if serializer.is_valid():
              serializer.save()
              return Response(serializer.data)
          return Response({
              'status' : 400,
              'data'  : serializer.errors
          })
        else:
          return Response({
            'status' : 400,
            'message' : "Error occured"
          })

    def delete(self, request, pk, format=None):
        userData = self.get_object(pk)
        userData.delete()
        return Response({
            'status' : 200,
            'message' : "Your account has been permanently deactivated"
        })


@api_view(['POST'])
# @authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'status': 'ok'})