from django.urls import path
from post.post.views import PostListAPIView, PostCreateAPIView, PostRetrieveUpdateDestroyAPIView, PostCommentsListView,\
    PostCommentCreateAPIView, PostCommentListCreateAPIView, CommentRetrieveView, CommentLikeListView, PostLikeListView,\
    PostLikeAPIView, CommentLikeAPIView
from post.profile.views import FollowAPIView

urlpatterns = [
    path('list/', PostListAPIView.as_view(), name='post_list'),
    path('create/', PostCreateAPIView.as_view(), name='post_create'),
    path('<uuid:pk>/', PostRetrieveUpdateDestroyAPIView.as_view()),
    path('<uuid:pk>/likes/', PostLikeListView.as_view()),
    path('<uuid:pk>/comments/', PostCommentsListView.as_view()),
    path('<uuid:pk>/comment/create/', PostCommentCreateAPIView.as_view()),

    path('comments/', PostCommentListCreateAPIView.as_view()),
    path('comments/<uuid:pk>/', CommentRetrieveView.as_view()),
    path('comments/<uuid:pk>/likes/', CommentLikeListView.as_view()),
    path('comments/<uuid:pk>/create-delete-like/', CommentLikeAPIView.as_view()),

    path('<uuid:pk>/create-delete-like/', PostLikeAPIView.as_view()),

    path('follow/', FollowAPIView.as_view()),

]