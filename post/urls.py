from django.urls import path
from .views import PostListAPIView

urlpatterns = [
    path('posts/', PostListAPIView.as_view(), name='post_list')
    ]