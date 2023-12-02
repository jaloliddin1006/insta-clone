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


class PostCommentsListView(generics.ListAPIView):
    serializer_class = PostCommentSerializer
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination

    def get_queryset(self):
        post_id = self.kwargs.get('pk')
        queryset =  PostComment.objects.filter(post__id=post_id).order_by('-created_at')
        return queryset


class PostCommentCreateAPIView(generics.CreateAPIView):
    serializer_class = PostCommentSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        post_id = self.kwargs.get('pk')
        post = Post.objects.get(id=post_id)
        serializer.save(author=self.request.user, post=post)


class PostCommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PostCommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination
    queryset = PostComment.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        post_id = self.request.data.get('post')
        print(post_id, "===============")
        if post_id:
            queryset = queryset.filter(post__id=post_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)