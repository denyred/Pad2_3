from rest_framework.views import APIView
from rest_framework import status, response
import time
import os
from users.models import User


class StatusView(APIView):
    def get(self, request):
        return response.Response(
            {'message': f"The instance of authenService running on {request.get_host()} is alive!"},
            status=status.HTTP_202_ACCEPTED
        )
    

class SleepyView(APIView):
    def get(self, request):
        time.sleep(int(os.getenv('SLEEP_DURATION_S')))

        return response.Response(
            {'message': "You are not supposed to see this message!"},
            status=status.HTTP_202_ACCEPTED
        )
    

class CheckUserIdView(APIView):

    def get(self, request):
        user_id = request.query_params.get('user_id')

        if not user_id:
            return response.Response(
                {'detail': "user_id to check was not provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)

            return response.Response(
                {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'user_type': user.user_type
                },
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return response.Response(
                {'detail': "User not found."},
                status=status.HTTP_400_BAD_REQUEST
            )