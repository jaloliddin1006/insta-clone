from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from shared.custom_pagination import CustomPagination
from . models import Post, PostComment, PostLike, CommentLike
from . serializer import PostSerializer, PostCommentSerializer


class PostListAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination

    def get_queryset(self):
        return Post.objects.all().order_by('-created_at')


class PostCreateAPIView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def put(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return Response(
                {
                    'success': False,
                    'status_code': status.HTTP_403_FORBIDDEN,
                    'message': 'Sen ushbu postni tahrirlay olmaysiz, chunki post senga tegishli emas',
                    'data': []
                }
            )
        serializer = self.serializer_class(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'success': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Post updated successfully',
                'data': serializer.data
            }
        )

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return Response(
                {
                    'success': False,
                    'status_code': status.HTTP_403_FORBIDDEN,
                    'message': 'Sen ushbu postni o\'chira olmaysan, chunki post senga tegishli emas',
                    'data': []
                }
            )
        post.delete()
        return Response(
            {
                'success': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Post deleted successfully',
                'data': []
            }
        )