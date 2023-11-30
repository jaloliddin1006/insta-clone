from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from . models import Post, PostComment, PostLike, CommentLike
from . serializer import PostSerializer, PostCommentSerializer


class PostListAPIView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (AllowAny,)