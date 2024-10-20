from rest_framework import serializers
from .models import Chat


class ChatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chat
        fields = ['id', 'customer_id', 'employee_id', 'identifier']

    def create(self, validated_data):
        return Chat.objects.create(**validated_data)


class ConnectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chat
        fields = ['connect_url']