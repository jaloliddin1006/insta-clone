from django.urls import path
from .views import CreateUserView, VerifyAPIView

urlpatterns = [
    path('signup/', CreateUserView.as_view()),
    path('verify/', VerifyAPIView.as_view()),
]