from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache
from chatService.permissions import get_user_info


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()

        self.identifier = self.scope['url_route']['kwargs']['identifier']
        self.chat_group_name = f'chat_{self.identifier}'

        # Extract auth. credentials
        self.user_id = self.get_user_id_from_headers(self.scope['headers'])

        if self.user_id is None:
            await self.send_error("No auth. credentials provided.")
            await self.close()
            return
        
        # Check user
        self.user_data = await self.check_user_data()
        if not self.user_data:
            await self.send_error("Invalid auth. credentials.")
            await self.close()
            return
        
        # Check registered in chat
        if not await self.check_registered_in_chat():
            await self.send_error("This is an unauthorized access attempt.")
            self.user_data = None
            await self.close()
            return

        # Join chat group
        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )

        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'chat_message',
                'message': f'{self.user_data['first_name']} {self.user_data['last_name'][0]}. has joined the conversation.'
            }
        )

    async def disconnect(self, close_code):
        if self.user_data:
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'chat_message',
                    'message': f'{self.user_data['first_name']} {self.user_data['last_name'][0]}. has left the conversation.'
                }
            )

            # Leave lobby group
            await self.channel_layer.group_discard(
                self.chat_group_name,
                self.channel_name
            )

    async def receive_json(self, content, **kwargs):
        type = content.get('type', '')
        message = content.get('message', '')

        # Send message to lobby group
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': type,
                'message': f'{self.user_data['first_name']} {self.user_data['last_name'][0]}. : {message}'
            }
        )

    async def chat_message(self, event):
        type = event['type']
        message = event['message']

        # Send message to WebSocket
        await self.send_json({
            'type': type,
            'message': message
        })

    def get_user_id_from_headers(self, headers):
        for key, value in headers:
            if key == b'x-user':
                return int(value.decode('utf-8'))  # Decode from bytes to string
        return None
    
    async def check_user_data(self):
        return get_user_info(self.user_id)
    
    def cache_user_data(self, user_id, user_data):
        cache.set(f"user_{user_id}_data", user_data, timeout=3600)
        print(f"ChatConsumer.check_user: Cached data for user#{user_id}")
    
    async def check_registered_in_chat(self):
        from chats.models import Chat

        try:
            chat = await database_sync_to_async(Chat.objects.get)(identifier=self.identifier)
            return self.user_id == chat.customer_id or self.user_id == chat.employee_id
        except Chat.DoesNotExist:
            return False

    async def send_error(self, error_message):
        await self.send_json({
            'type': 'error',
            'detail': error_message
        })