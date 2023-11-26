from django.urls import path
from .views import CreateUserView

urlpatterns = [
    path('signup/', CreateUserView.as_view()),
]