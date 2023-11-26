from shared.utilits import check_email_or_phone, send_mail_code, send_phone_code
from .models import User, UserConfirmation, VIA_EMAIL, VIA_PHONE, NEW, CODE_VERIFIED, DONE, PHOTO_STEP
from rest_framework import serializers, exceptions
from rest_framework.exceptions import ValidationError
from django.db.models import Q


class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required=False)

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
