from rest_framework import generics, views
from .models import User
from .serializers import UserSerializer, EmployeeListSerializer
from rest_framework import status, response


# View to list all users
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# View to list employees only
class EmployeeListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = EmployeeListSerializer

    def get_queryset(self):
        return User.objects.filter(user_type=User.EMPLOYEE)


# View to delete a user by ID
class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'  # This ensures the user is deleted based on ID


# View to patch employee rating
class PatchEmployeeRatingView(views.APIView):

    def patch(self, request):
        
        # Get user_id and rating from query parameters
        user_id = request.query_params.get('user_id')
        rating = request.query_params.get('new_rating')

        if not user_id or not rating:
            return response.Response(
                {"detail": "Both user_id and new_rating are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate rating as a float
        try:
            rating = float(rating)
        except ValueError:
            return response.Response(
                {"detail": "Rating must be a valid number."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate that the rating is between 0 and 5
        if rating < 0 or rating > 5:
            return response.Response(
                {"detail": "Rating must be between 0 and 5."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Try to retrieve the user by ID
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return response.Response(
                {'detail': "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if the user is an employee
        if user.user_type != User.EMPLOYEE:
            return response.Response(
                {'detail': "This is invalid transaction."},
                status=status.HTTP_403_FORBIDDEN
            )
 
        # Update the user's rating
        user.rating = rating
        user.save()

        return response.Response(
            {
                "message": "Rating updated successfully.",
                "new_rating": user.rating
            }, 
            status=status.HTTP_200_OK
        )