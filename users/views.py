from rest_framework import permissions
from rest_framework.decorators import permission_classes
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.datetime_safe import datetime
from rest_framework.exceptions import ValidationError

from shared.utilits import send_mail_code
from .models import User, CODE_VERIFIED, DONE, NEW, VIA_EMAIL, VIA_PHONE
from .serializers import SignUpSerializer, ChangeUserInformationSerializer

class CreateUserView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = (permissions.AllowAny, )



class VerifyAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        user = request.user
        code = request.data.get('code')
        self.check_verify_code(user, code)
        context = {
            "status": "success",
            'message': 'Sizning akkauntingiz tasdiqlandi',
            'access_token': user.token()['access'],
            'refresh_token': user.token()['refresh_token'],
        }
        return Response(context)

    @staticmethod
    def check_verify_code(user, code):
        verifies = user.user_codes.filter(expiration_time__gte=datetime.now(), code=code, is_confirmation=False)
        if not verifies.exists():
            context = {
                "status": "error",
                'message': 'Kod noto\'g\'ri kiritildi yoki eskirgan'
            }
            raise ValidationError(context)
        else:
            verifies.update(is_confirmation=True)

        if user.auth_status == NEW:
            user.auth_status = CODE_VERIFIED
            user.save()

        return True


class GetNewVerifyCodeAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        user = request.user
        self.chccknew_verify_code(user)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_mail_code(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_mail_code(user.email, code)
            # send_phone_code(user.phone, code)
        else:
            context = {
                "status": "error",
                'message': 'Email yoki telefon raqam kiritilmagan'
            }
            raise ValidationError(context)

        context = {
            "status": "success",
            'message': 'Yangi kod yuborildi',
        }
        return Response(context)

    @staticmethod
    def chccknew_verify_code(user):
        verifies = user.user_codes.filter(expiration_time__gte=datetime.now(), is_confirmation=False)
        if verifies.exists():
            context = {
                "status": "error",
                'message': 'Kod hali amal qilinmoqda'
            }
            raise ValidationError(context)
        return True


class ChangeUserInformationView(UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ChangeUserInformationSerializer
    http_method_names = ['put', 'patch']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        super(ChangeUserInformationView, self).update(request, *args, **kwargs)
        context = {
            "status": "success",
            'message': 'Ma\'lumotlar <put> bilan o\'zgartirildi',
            'auth_status': request.user.auth_status,
        }

        return Response(context, status=200)

    def partial_update(self, request, *args, **kwargs):
        super(ChangeUserInformationView, self).partial_update(request, *args, **kwargs)
        context = {
            "status": "success",
            'message': 'Ma\'lumotlar <putch> bilan o\'zgartirildi',
            'auth_status': request.user.auth_status,
        }

        return Response(context, status=200)
