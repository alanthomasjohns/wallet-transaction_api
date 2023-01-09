from django.urls import path
from .views import UserChangePasswordView, UserLoginView, UserProfileView, UserRegistrationView, UserDetails
from . import views
urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('userDetails/<int:pk>/', UserDetails.as_view()),
    path('logout/', views.logout_view, name='logout'),

]