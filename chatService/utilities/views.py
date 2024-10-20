from rest_framework.views import APIView
from rest_framework import status, response


class StatusView(APIView):
    def get(self, request):
        return response.Response(
            {'message': f"The instance of chatService running on {request.get_host()} is alive!"},
            status=status.HTTP_202_ACCEPTED
        )