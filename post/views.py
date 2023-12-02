from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.custom_pagination import CustomPagination
from . models import Post, PostComment, PostLike, CommentLike
from .serializer import PostSerializer, PostCommentSerializer, CommentLikeSerializer, PostLikeSerializer


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


class CommentRetrieveView(generics.RetrieveAPIView):
    queryset = PostComment.objects.all()
    serializer_class = PostCommentSerializer
    permission_classes = (AllowAny,)


class PostLikeListView(generics.ListAPIView):
    serializer_class = PostLikeSerializer
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination

    def get_queryset(self):
        post_id = self.kwargs.get('pk')
        queryset = PostLike.objects.filter(post__id=post_id).order_by('-created_at')
        return queryset


class CommentLikeListView(generics.ListAPIView):
    serializer_class = CommentLikeSerializer
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination

    def get_queryset(self):
        comment_id = self.kwargs.get('pk')
        queryset = CommentLike.objects.filter(comment__id=comment_id).order_by('-created_at')
        return queryset


class PostLikeAPIView(APIView):
    def post(self, request, pk):
        try:
            is_like = PostLike.objects.filter(
                author=request.user,
                post_id=pk
            ).exists()
            if is_like:
                return Response(
                    {
                        'success': False,
                        'status_code': status.HTTP_400_BAD_REQUEST,
                        'message': 'Siz ushbu postga like bosganingiz mazgi :)',
                        'data': []
                    }
                )

            post_like = PostLike.objects.create(
                author=request.user,
                post_id=pk
            )
            serializer = PostLikeSerializer(post_like)
            return Response(
                {
                    'success': True,
                    'status_code': status.HTTP_201_CREATED,
                    'message': 'Malades siz like bosdingiz mazgi :)',
                    'data': serializer.data
                }
            )
        except Exception as err:
            return Response(
                {
                    'success': False,
                    'status_code': status.HTTP_400_BAD_REQUEST,
                    'message': f"{err}",
                    'data': []
                }
            )

    def delete(self, requset, pk):
        try:
            post_like = PostLike.objects.get(
                author=requset.user,
                post_id=pk
            )
            post_like.delete()
            return Response(
                {
                    'success': True,
                    'status_code': status.HTTP_200_OK,
                    'message': 'Bosgan LIKE ingiz o\'chdi mazgi :(',
                    'data': []
                }
            )
        except Exception as err:
            return Response(
                {
                    'success': False,
                    'status_code': status.HTTP_400_BAD_REQUEST,
                    'message': f"{err}",
                    'data': []
                }
            )



class CommentLikeAPIView(APIView):
    def post(self, request, pk):
        try:
            is_like = CommentLike.objects.filter(
                author=request.user,
                comment_id=pk
            ).exists()
            if is_like:
                return Response(
                    {
                        'success': False,
                        'status_code': status.HTTP_400_BAD_REQUEST,
                        'message': 'Siz ushbu izohga like bosganingiz mazgi :)',
                        'data': []
                    }
                )

            comment_like = CommentLike.objects.create(
                author=request.user,
                comment_id=pk
            )
            serializer = CommentLikeSerializer(comment_like)
            return Response(
                {
                    'success': True,
                    'status_code': status.HTTP_201_CREATED,
                    'message': 'Malades siz izohga like bosdingiz mazgi :)',
                    'data': serializer.data
                }
            )
        except Exception as err:
            return Response(
                {
                    'success': False,
                    'status_code': status.HTTP_400_BAD_REQUEST,
                    'message': f"{err}",
                    'data': []
                }
            )

    def delete(self, requset, pk):
        try:
            comment_like = CommentLike.objects.get(
                author=requset.user,
                comment_id=pk
            )
            comment_like.delete()
            return Response(
                {
                    'success': True,
                    'status_code': status.HTTP_200_OK,
                    'message': 'Bosgan LIKE ingiz o\'chdi mazgi :(',
                    'data': []
                }
            )
        except Exception as err:
            return Response(
                {
                    'success': False,
                    'status_code': status.HTTP_400_BAD_REQUEST,
                    'message': f"{err}",
                    'data': []
                })

