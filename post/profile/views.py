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
        follow_id = request.data.get('user_id')

        follow = user.user_followers.filter(follower_id=follow_id)
        if follow.exists():
            follow.delete()
            context = {
                "status": True,
                'message': 'Siz obunani bekor qildingiz',
                'access_token': user.token()['access'],
                'refresh_token': user.token()['refresh_token'],
            }
            return Response(context, status=200)


        if user.id == follow_id:
            context = {
                "status": "error",
                'message': 'Siz o\'zingizga obuna bo\'la olmaysiz'
            }
            return Response(context)


        follow = Follow.objects.create(user=user, follower_id=follow_id)
        follow.save()

        context = {
            "status": True,
            'message': 'Sizning follow bosdingiz',
            'access_token': user.token()['access'],
            'refresh_token': user.token()['refresh_token'],
        }
        return Response(context, status=201)
