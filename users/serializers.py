from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.serializers import TokenObtainSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from post.post.serializer import PostSerializer
from shared.utilits import check_email_or_phone, send_mail_code, send_phone_code, check_user_type
from .models import User, VIA_EMAIL, VIA_PHONE, CODE_VERIFIED, DONE, PHOTO_STEP
from rest_framework import serializers, exceptions
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from django.db.models import Q


class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('id', 'auth_type', 'auth_status')
        extra_kwargs = {
            'auth_type': {'read_only': True, "required": False},
            'auth_status': {'read_only': True, "required": False},
        }

    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)

        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(verify_type=VIA_EMAIL)
            send_mail_code(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(verify_type=VIA_PHONE)
            send_mail_code(user.phone, code)
            # send_phone_code(user.phone, code)
        else:
            raise exceptions.ValidationError("auth_type not defined")
        user.save()
        return user

    def validate(self, data):
        super(SignUpSerializer, self).validate(data)
        data = self.auth_validate(data)
        return data

    @staticmethod
    def auth_validate(data):
        user_input = str(data.get('email_phone_number')).lower()
        input_type = check_email_or_phone(user_input)
        if input_type == "email":
            data = {
                'email': user_input,
                'auth_type': VIA_EMAIL,
            }
        elif input_type == "phone":
            data = {
                'phone': user_input,
                'auth_type': VIA_PHONE,
            }
        else:
            context = {
                "status": "error",
                'message': 'email yoki telefon raqam noto\'g\'ri kiritildi'
            }
            raise ValidationError(context)
        return data

    def validate_email_phone_number(self, value):
        value = str(value).lower()
        print("validate_email_or_phone", value)
        if value and User.objects.filter(email=value).exists():
            data = {
                "status": "error",
                'message': 'Email allaqcachon ro\'yxatdan o\'tgan'
            }
            raise exceptions.ValidationError(data)
        elif value and User.objects.filter(phone=value).exists():
            data = {
                "status": "error",
                'message': 'Telefon raqam allaqcachon ro\'yxatdan o\'tgan'
            }
            raise exceptions.ValidationError(data)

        return value

    def to_representation(self, instance):
        print("to_representation", instance)
        data = super(SignUpSerializer, self).to_representation(instance)
        data.update(instance.token())
        return data


class ChangeUserInformationSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    username = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            context = {
                "status": "error",
                'message': 'Parollar mos kelmadi'
            }
            raise exceptions.ValidationError(context)

        if password:
            validate_password(password)
            validate_password(confirm_password)
        return data

    def validate_username(self, username):
        if len(username) < 5 or len(username) > 30:
            context = {
                "status": "error",
                'message': 'Username 5 ta belgidan kam va 30 belgidan ko\'p bo\'lmasligi kerak'
            }
            raise exceptions.ValidationError(context)

        if username.isdigit():
            raise exceptions.ValidationError("Username faqat raqamdan iborat bo\'lmasligi kerak")

        return username

    def validate_first_name(self, first_name):
        if len(first_name) < 2 or len(first_name) > 35:
            raise exceptions.ValidationError("Ism 2 ta belgidan kam va 35 belgidan ko\'p bo\'lmasligi kerak")
        if first_name.isdigit():
            raise exceptions.ValidationError("Ism raqamdan iborat bo\'lmasligi kerak")
        if not first_name.isalpha():
            raise exceptions.ValidationError("Ism faqat harflardan iborat bo\'lishi kerak")
        return first_name

    def validate_last_name(self, last_name):
        if len(last_name) < 2 or len(last_name) > 35:
            raise exceptions.ValidationError("Familya 2 ta belgidan kam va 35 belgidan ko\'p bo\'lmasligi kerak")
        if last_name.isdigit():
            raise exceptions.ValidationError("Familya raqamdan iborat bo\'lmasligi kerak")
        if not last_name.isalpha():
            raise exceptions.ValidationError("Familya faqat harflardan iborat bo\'lishi kerak")
        return last_name

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name')
        instance.last_name = validated_data.get('last_name')
        instance.username = validated_data.get('username')
        instance.set_password(validated_data.get('password'))
        if instance.auth_status == CODE_VERIFIED:
            instance.auth_status = DONE
        instance.save()
        return instance


class ChangeUserPhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField(validators=[
        FileExtensionValidator(
            allowed_extensions=['png', 'jpg', 'jpeg', 'heic']
        )])

    def update(self, instance, validated_data):
        avatar = validated_data.get('photo')
        if avatar:
            instance.avatar = avatar
            instance.auth_status = PHOTO_STEP
            instance.save()
        return instance


class LoginSerializer(TokenObtainSerializer):
    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.fields['userinput'] = serializers.CharField(required=True)
        self.fields['username'] = serializers.CharField(required=False, read_only=True)

    def auth_validate(self, data):
        user_input = str(data.get('userinput')).lower()
        input_type = check_user_type(user_input)
        if input_type == "username":
            username = user_input
        elif input_type == "email":
            username = self.get_user(email__iexact=user_input).username
        elif input_type == "phone":
            username = self.get_user(phone=user_input).username
        else:
            context = {
                "status": "error",
                'message': 'login noto\'g\'ri kiritildi'
            }
            raise ValidationError(context)

        authentication_kwargs = {
            self.username_field: username,
            'password': data.get('password')
        }

        current_user = User.objects.filter(username=username).first() ### bu usul xato, chunki ro'yxatdan to'liq o'tmagan bo'lsa username bo'yicha qidirib topmaydi
        if current_user is None or current_user.auth_status not in [DONE, PHOTO_STEP]:
            context = {
                "status": False,
                'message': 'Sizning akkauntingiz tasdiqlanmagan. To\'liq ro\'yxatdan o\'ting'
            }
            raise ValidationError(context)

        user = authenticate(**authentication_kwargs)

        if user is not None:
            self.user = user
        else:
            context = {
                "status": False,
                'message': 'login yoki parol noto\'g\'ri'
            }
            raise ValidationError(context)
    def validate(self, data):
        self.auth_validate(data)
        if self.user.auth_status not in [DONE, PHOTO_STEP]:
            context = {
                "status": False,
                'message': 'Sizning akkauntingiz tasdiqlanmagan. To\'liq ro\'yxatdan o\'ting'
            }
            raise PermissionDenied(context)
        data = self.user.token()
        data['auth_status'] = self.user.auth_status
        data["full_name"] = self.user.full_name
        return data

    def get_user(self, **kwargs):
        user = User.objects.filter(**kwargs)
        if not user.exists():
            context = {
                "status": "error",
                'message': 'login yoki parol noto\'g\'ri'
            }
            raise ValidationError(context)
        return user.first()


class LoginRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super(self).validate(attrs)
        access_token_instance = AccessToken(data['access'])
        user_id = access_token_instance['user_id']
        user = get_object_or_404(User, id=user_id)
        update_last_login(None, user)
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email_or_phone = attrs.get('email_or_phone')
        if email_or_phone is None:
            context = {
                "status": "error",
                'message': 'email yoki telefon raqam kiritilmadi'
            }
            raise ValidationError(context)
        user_input = str(email_or_phone).lower()
        user = User.objects.filter(Q(email=user_input) | Q(phone=user_input))
        if not user.exists():
            raise NotFound(detail="Bunday user topilmadi")

        attrs['user'] = user.first()
        return attrs


class UserProfileViewSerializer(serializers.ModelSerializer):

    is_followed = serializers.SerializerMethodField('get_is_followed')
    followers_count = serializers.SerializerMethodField('get_followers_count')
    following_count = serializers.SerializerMethodField('get_following_count')
    posts_count = serializers.SerializerMethodField('get_posts_count')

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'avatar', 'phone', 'email', 'is_followed', 'followers_count', 'following_count', 'posts_count', 'created_at')

    def get_is_followed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            author_post = obj
            user = get_object_or_404(User, pk=request.user.pk)
            return author_post.user_followers.filter(follower=user).exists()
        return False

    @staticmethod
    def get_followers_count(obj):
        return obj.user_followers.count()

    @staticmethod
    def get_following_count(obj):
        return obj.user_followings.count()

    @staticmethod
    def get_posts_count(obj):
        return obj.user_posts.count()
    #
    # @staticmethod
    # def get_user_posts(obj):
    #     return PostSerializer(obj.user_posts.all()).data



