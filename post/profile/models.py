from django.db import models
from shared.models import SharedModel
from users.models import User


class Follow(SharedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_followers',
                             verbose_name='user')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_followings',
                                 verbose_name='follower')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'follower'], name='unique_follow')
        ]

    def __str__(self):
        return f"{self.user} - {self.follower}"
