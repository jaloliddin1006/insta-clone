from rest_framework import serializers
from post.models import Post, PostComment, PostLike, CommentLike
from users.models import User


class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'profile_image')


class PostSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = GetUserSerializer(read_only=True)
    post_likes_count = serializers.SerializerMethodField('get_post_likes_count')
    post_comments_count = serializers.SerializerMethodField('get_post_comments_count')
    is_liked = serializers.SerializerMethodField('get_is_liked')

    class Meta:
        model = Post
        fields = ('id', 'author', 'image', 'caption',
                  'created_at', 'post_likes_count',
                  'post_comments_count', 'is_liked', )

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
        fields = ('id', 'author', 'comment', 'parent',  'created_at', 'replies', 'comment_likes_count', 'is_liked')

    def get_replies(self, obj):
        if obj.child.exists():
            serializer = self.__class__(obj.child.all(), many=True, context=self.context)
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

    class Meta:
        model = CommentLike
        fields = ('id', 'author', 'comment')


class PostLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = GetUserSerializer(read_only=True)

    class Meta:
        model = PostLike
        fields = ('id', 'author', 'post')
