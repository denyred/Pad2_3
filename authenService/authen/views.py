from rest_framework.views import APIView
from users.models import User
from users.serializers import UserSerializer
from rest_framework import status, generics, response


class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)

        return response.Response(
            {'detail': 'Successfully registered.'},
            status=status.HTTP_201_CREATED
        )


class SignInView(APIView):

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return response.Response(
                {'detail': "Invalid credentials."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if user.password != password:
            return response.Response(
                {'detail': "Invalid credentials."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return response.Response(
            {'user_id': user.id},
            status=status.HTTP_200_OK
        )