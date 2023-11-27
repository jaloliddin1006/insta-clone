from rest_framework import permissions
from rest_framework.decorators import permission_classes
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.datetime_safe import datetime
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from shared.utilits import send_mail_code
from .models import User, CODE_VERIFIED, DONE, NEW, VIA_EMAIL, VIA_PHONE
from .serializers import SignUpSerializer, ChangeUserInformationSerializer, ChangeUserPhotoSerializer, LoginSerializer, \
    LoginRefreshSerializer


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

    def get_object(self, *args, **kwargs):
        user = get_object_or_404(User, pk=self.request.user.pk)
        return user

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


class ChangeUserPhotoView(UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated, )

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = ChangeUserPhotoSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.update(user, serializer.validated_data)

            context = {
                "status": "success",
                'message': 'Rasm muvaffaqiyatli o\'zgartirildi',
                'auth_status': user.auth_status,
            }
            return Response(context, status=200)
        return Response(serializer.errors, status=400)


class LoginAPIView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny, )
    http_method_names = ['post', ]

class LoginRefreshView(TokenRefreshView):
    permission_classes = (permissions.AllowAny, )
    http_method_names = ['post', ]
    serializer_class = LoginRefreshSerializer