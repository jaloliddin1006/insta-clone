from django.shortcuts import get_object_or_404
from rest_framework import serializers
from post.post.models import Post, PostComment, PostLike, CommentLike
from post.profile.models import Follow
from users.models import User


class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'avatar')


class PostSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = GetUserSerializer(read_only=True)
    post_likes_count = serializers.SerializerMethodField('get_post_likes_count')
    post_comments_count = serializers.SerializerMethodField('get_post_comments_count')
    is_liked = serializers.SerializerMethodField('get_is_liked')
    is_followed = serializers.SerializerMethodField('get_is_followed')

    extra_kwargs = {
        'image': {'required': False}
    }

    class Meta:
        model = Post
        fields = ('id', 'author', 'image', 'caption',
                  'created_at', 'post_likes_count',
                  'post_comments_count', 'is_liked', 'is_followed', )

    def get_is_followed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            author_post = obj.author
            user = get_object_or_404(User, pk=request.user.pk)
            return author_post.user_followers.filter(follower=user).exists()
        return False

    @staticmethod
    def get_post_likes_count(obj):
        return obj.post_likes.count()

    @staticmethod
    def get_post_comments_count(obj):
        return obj.post_comments.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.post_likes.filter(author=request.user).exists()
        return False


class PostCommentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = GetUserSerializer(read_only=True)
    replies = serializers.SerializerMethodField('get_replies')
    comment_likes_count = serializers.SerializerMethodField('get_comment_likes_count')
    is_liked = serializers.SerializerMethodField('get_is_liked')

    class Meta:
        model = PostComment
        fields = ('id', 'author', 'post', 'comment', 'parent',  'created_at', 'replies', 'comment_likes_count', 'is_liked')

    def get_replies(self, obj):
        if obj.replies.exists():
            serializer = self.__class__(obj.replies.all(), many=True, context=self.context)
            return serializer.data
        return None

    @staticmethod
    def get_comment_likes_count(obj):
        return obj.comment_likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.comment_likes.filter(author=request.user).exists()
        return False


class CommentLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = GetUserSerializer(read_only=True)
    is_followed = serializers.SerializerMethodField('get_is_followed')

    class Meta:
        model = CommentLike
        fields = ('id', 'author', 'comment', 'is_followed')

    def get_is_followed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            author_comment = obj.comment.author
            return author_comment.user_followings.filter(follower=request.user).exists()
        return False


class PostLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = GetUserSerializer(read_only=True)
    is_followed = serializers.SerializerMethodField('get_is_followed')

    class Meta:
        model = PostLike
        fields = ('id', 'author', 'post', 'is_followed')

    def get_is_followed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            author_post = obj.author
            user = get_object_or_404(User, pk=request.user.pk)
            return author_post.user_followers.filter(follower=user).exists()
        return False
