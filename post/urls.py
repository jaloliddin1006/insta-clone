from django.urls import path
from .views import PostListAPIView, PostCreateAPIView, PostRetrieveUpdateDestroyAPIView, PostCommentsListView,\
    PostCommentCreateAPIView

urlpatterns = [
    path('posts/', PostListAPIView.as_view(), name='post_list'),
    path('create/', PostCreateAPIView.as_view(), name='post_create'),
    path('post/<uuid:pk>/', PostRetrieveUpdateDestroyAPIView.as_view()),
    path('post/<uuid:pk>/comments/', PostCommentsListView.as_view()),
    path('post/<uuid:pk>/comment/create/', PostCommentCreateAPIView.as_view()),

]