from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from post.profile.models import Follow


class FollowAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    queryset = Follow.objects.all()

    def post(self, request, *args, **kwargs):
        user = request.user
        follow_id = request.data.get('follow_id')
        self.check_follow(user, follow_id)
        context = {
            "status": "success",
            'message': 'Sizning akkauntingiz tasdiqlandi',
            'access_token': user.token()['access'],
            'refresh_token': user.token()['refresh_token'],
        }
        return Response(context)

    @staticmethod
    def check_follow(user, follow_id):
        follow = user.user_followings.filter(follower_id=follow_id)
        if follow.exists():
            context = {
                "status": "error",
                'message': 'Siz allaqachon ushbu akkauntga obuna bo\'lgansiz'
            }
            raise ValidationError(context)

        if user.id == follow_id:
            context = {
                "status": "error",
                'message': 'Siz o\'zingizga obuna bo\'la olmaysiz'
            }
            raise ValidationError(context)

        else:
            follow = Follow.objects.create(user=user, follower_id=follow_id)
            follow.save()

        return True