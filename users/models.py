import uuid
from random import random

from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken

from shared.models import SharedModel
from datetime import datetime, timedelta

ORDINARY_USER, MANAGER, ADMIN = 'user', 'manager', 'admin'
VIA_EMAIL, VIA_PHONE = 'email', 'phone'
NEW, CODE_VERIFIED, DONE, PHOTO_STEP = 'new', 'code_verified', 'done', 'photo_step'





class User(AbstractUser, SharedModel):
    USER_ROLE_CHOICES = (
        (ORDINARY_USER, ORDINARY_USER),
        (MANAGER, MANAGER),
        (ADMIN, ADMIN)
    )
    AUTH_TYPE_CHOICES = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE)
    )
    AUTH_STATUS_CHOICES = (
        (NEW, NEW),
        (CODE_VERIFIED, CODE_VERIFIED),
        (DONE, DONE),
        (PHOTO_STEP, PHOTO_STEP)
    )
    user_role = models.CharField(max_length=30, choices=USER_ROLE_CHOICES, default='user')
    auth_type = models.CharField(max_length=30, choices=AUTH_TYPE_CHOICES)
    auth_status = models.CharField(max_length=30, choices=AUTH_STATUS_CHOICES, default='new')
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=13, unique=True, null=True, blank=True)
    avatar = models.ImageField(upload_to='user_avatars/', null=True, blank=True, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'heic'])])

    def __str__(self):
        return self.username

    def create_verify_code(self, verify_type):
        code = "".join([str(random.randint(0, 9)) for _ in range(4)])
        UserConfirmation.objects.create(user=self, verify_type=verify_type, code=code)
        return code

    def check_username(self):
        if not self.username:
            temp_username = f"instagram-{uuid.uuid4().__str__().split('-')[-1]}"
            while User.objects.filter(username=temp_username).exists():
                temp_username = f"{temp_username}-{uuid.uuid4().__str__().split('-')[0]}"
            self.username = temp_username

    def check_email(self):
        if self.email:
            normalize_email = self.email.lower()
            self.email = normalize_email

    def check_password(self):
        if not self.password:
            temp_password = f"{uuid.uuid4().__str__().split('-')[-1]}"
            self.password = temp_password

    def hash_password(self):
        if not self.password.startswith('pbkdf2_sha256$'):
            self.set_password(self.password)

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh_token': str(refresh),
            'access': str(refresh.access_token)
        }

    def clean(self):
        self.check_username()
        self.check_email()
        self.check_password()
        self.hash_password()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.clean()
        super(User, self).save(*args, **kwargs)
PHONE_EXPIRE_TIME = 2
EMAIL_EXPIRE_TIME = 5
class UserConfirmation(SharedModel):
    TYPE_CHOICES = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE)
    )
    verify_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_codes')
    code = models.CharField(max_length=4)
    expiration_time = models.DateTimeField(null=True, blank=True)
    is_confirmation = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.__str__())

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.verify_type == VIA_EMAIL:
                self.expiration_time = datetime.now() + timedelta(minutes=EMAIL_EXPIRE_TIME)
            elif self.verify_type == VIA_PHONE:
                self.expiration_time = datetime.now() + timedelta(minutes=PHONE_EXPIRE_TIME)

        super(UserConfirmation, self).save(*args, **kwargs)
