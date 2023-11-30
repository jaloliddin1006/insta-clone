from django.contrib import admin
from .models import Post, PostComment, PostLike, CommentLike


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'caption', 'created_at', 'updated_at')
    list_display_links = ('id', 'author')
    search_fields = ('author__username', 'caption')


class PostCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'post', 'comment', 'parent', 'created_at', 'updated_at')
    list_display_links = ('id', 'author')
    search_fields = ('author__username', 'comment')


class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'post', 'created_at', 'updated_at')
    list_display_links = ('id', 'author')
    search_fields = ('author__username',)


class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'comment', 'created_at', 'updated_at')
    list_display_links = ('id', 'author')
    search_fields = ('author__username',)


admin.site.register(Post, PostAdmin)
admin.site.register(PostComment, PostCommentAdmin)
admin.site.register(PostLike, PostLikeAdmin)
admin.site.register(CommentLike, CommentLikeAdmin)

