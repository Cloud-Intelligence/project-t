import json

from rest_framework import permissions, viewsets
from rest_framework.response import Response

from chat.models import Chat
from chat.serializers import ChatSerializer
from .utils import run_llm, to_markdown


class ChatViewSet(viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Chat.objects.all().order_by('-created_date')
    serializer_class = ChatSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.all().order_by('-created_date')

    # @action(detail=True, methods=['post'])
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        message = request.data.get("message")
        history = json.loads(instance.history if instance.history else "[]")

        print(f"Got new message: {message}")
        history.append({"role": "user", "parts": [message]})
        instance.history = json.dumps(history)

        context = request.data.get("context", instance.context)
        instance.context = request.data.get("context", instance.context)

        llm_result = call_llm(history, context)
        print(f"LLM Result: {llm_result}")

        history.append({"role": "model", "parts": [llm_result]})
        instance.history = json.dumps(history)
        instance.save()

        return Response({"message_html": to_markdown(llm_result)})


def call_llm(message_history, context):
    llm_result = run_llm(message_history, context)
    return llm_result
