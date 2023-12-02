from django.urls import path
from .views import PostListAPIView, PostCreateAPIView, PostRetrieveUpdateDestroyAPIView, PostCommentsListView,\
    PostCommentCreateAPIView, PostCommentListCreateAPIView

urlpatterns = [
    path('list/', PostListAPIView.as_view(), name='post_list'),
    path('create/', PostCreateAPIView.as_view(), name='post_create'),
    path('<uuid:pk>/', PostRetrieveUpdateDestroyAPIView.as_view()),
    path('<uuid:pk>/comments/', PostCommentsListView.as_view()),
    path('<uuid:pk>/comment/create/', PostCommentCreateAPIView.as_view()),
    path('comments/', PostCommentListCreateAPIView.as_view()),

]