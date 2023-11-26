from rest_framework import permissions
from rest_framework.decorators import permission_classes
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.datetime_safe import datetime
from rest_framework.exceptions import ValidationError
from .models import User, CODE_VERIFIED, DONE, NEW
from .serializers import SignUpSerializer

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