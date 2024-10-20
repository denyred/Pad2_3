from rest_framework import generics, response, status
from .serializers import ChatSerializer, ConnectSerializer
from .models import Chat
from chatService.permissions import CheckUserWithAuthenService
from django.db.models import Q
from chatService.permissions import get_user_info


# View to list all chats
class ChatListView(generics.ListAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer


# View all the chats in which user is either customer or employee
class ChatListMyView(generics.ListAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    permission_classes = [CheckUserWithAuthenService]

    def get_queryset(self):
        user_id = self.request.user_data.get('id')

        # Query for chats where the user is either the customer or employee
        return Chat.objects.filter(
            Q(customer_id=user_id) | Q(employee_id=user_id)
        )


# View to delete a chat by ID
class ChatDeleteView(generics.DestroyAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    lookup_field = 'id'  # This ensures the chat is deleted based on ID


# Create a chat room for customer and employee
class StartChatView(generics.CreateAPIView):
    permission_classes = [CheckUserWithAuthenService]

    def post(self, request):
        user_type = self.request.user_data.get('user_type')
        if user_type != 'customer':
            return response.Response(
                {"detail": "You are not allowed to do that."},
                status=status.HTTP_403_FORBIDDEN
            )

        customer_id = self.request.user_data.get('id')
        employee_id = self.request.query_params.get('employee_id')
        if not employee_id:
            return response.Response(
                {'detail': "employee_id is required in query parameters."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            employee_id = int(employee_id)
        except ValueError:
            return response.Response(
                {'detail': "employee_id must be an integer."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        employee_data = get_user_info(employee_id)
        if not employee_data:
            return response.Response(
                {'detail': "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if employee_data['user_type'] != 'employee':
            return response.Response(
                {'detail': "This is invalid transaction."},
                status=status.HTTP_404_NOT_FOUND
            )

        chat_data = {
            'customer_id': customer_id,
            'employee_id': employee_id
        }
        
        serializer = ChatSerializer(data=chat_data)

        # Validate and save the data
        if serializer.is_valid():
            chat = serializer.save()
            
            return response.Response(
                {'connect_url': chat.connect_url}, 
                status=status.HTTP_201_CREATED
            )
        
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ChatConnectView(generics.ListAPIView):
    queryset = Chat.objects.all()
    serializer_class = ConnectSerializer
    def get_queryset(self):
        chat_id = self.request.query_params.get('id')

        # Filter the queryset by 'id' if it's provided
        if chat_id is not None:
            return self.queryset.filter(id=chat_id)

        # If 'id' is not provided, return an empty queryset
        return self.queryset.none()