from django.urls import path
from .views import PostListAPIView, PostCreateAPIView, PostRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('posts/', PostListAPIView.as_view(), name='post_list'),
    path('create/', PostCreateAPIView.as_view(), name='post_create'),
    path('post/<uuid:pk>/', PostRetrieveUpdateDestroyAPIView.as_view(), name='post_update'),
]