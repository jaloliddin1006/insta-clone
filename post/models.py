from django.core.validators import MaxLengthValidator, FileExtensionValidator
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.constraints import UniqueConstraint

from shared.models import SharedModel


User = get_user_model()


class Post(SharedModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_posts')
    image = models.ImageField(upload_to='post_images/', validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'heic'])])
    caption = models.TextField(validators=[MaxLengthValidator(2000)])

    class Meta:
        # db_table = 'posts'
        verbose_name = 'post'
        verbose_name_plural = 'posts'

    def __str__(self):
        return f" {self.author.username} - {self.id}"


class PostComment(SharedModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comments')
    comment = models.TextField(validators=[MaxLengthValidator(200)])
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'post_comment'
        verbose_name_plural = 'post_comments'

    def __str__(self):
        return f"{self.post} - {self.comment} "


class PostLike(SharedModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['author', 'post'],
                name='unique_post_like')
        ]

    def __str__(self):
        return f"{self.post} - {self.author}"


class CommentLike(SharedModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comment_likes')
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, related_name='comment_likes')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['author', 'comment'],
                name='unique_comment_like')
        ]

    def __str__(self):
        return f"{self.comment} - {self.author}"