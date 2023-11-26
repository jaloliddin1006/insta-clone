from django.urls import path
from .views import CreateUserView, VerifyAPIView, GetNewVerifyCodeAPIView, ChangeUserInformationView

urlpatterns = [
    path('signup/', CreateUserView.as_view()),
    path('verify/', VerifyAPIView.as_view()),
    path('new-verify/', GetNewVerifyCodeAPIView.as_view()),
    path('change-user/', ChangeUserInformationView.as_view()),
]