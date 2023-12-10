from django.urls import path
from .views import CreateUserView, VerifyAPIView, GetNewVerifyCodeAPIView, ChangeUserInformationView, ChangeUserPhotoView,\
    LoginAPIView, TokenRefreshView, LogoutView, ForgotPasswordView, UserProfileView

urlpatterns = [
    path('<str:username>/', UserProfileView.as_view()),
    path('login/', LoginAPIView.as_view()),
    path('login/refresh/', TokenRefreshView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('signup/', CreateUserView.as_view()),
    path('verify/', VerifyAPIView.as_view()),
    path('new-verify/', GetNewVerifyCodeAPIView.as_view()),
    path('change-user/', ChangeUserInformationView.as_view()),
    path('change-user-photo/', ChangeUserPhotoView.as_view()),
    path('forgot-password/', ForgotPasswordView.as_view()),
]