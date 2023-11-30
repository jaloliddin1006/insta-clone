from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny

from shared.custom_pagination import CustomPagination
from . models import Post, PostComment, PostLike, CommentLike
from . serializer import PostSerializer, PostCommentSerializer


class PostListAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination

    def get_queryset(self):
        return Post.objects.all().order_by('-created_at')