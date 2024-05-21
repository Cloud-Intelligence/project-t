from rest_framework import serializers


class ChatSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=255)
    context = serializers.CharField(max_length=255)
