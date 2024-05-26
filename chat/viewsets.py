import json

from rest_framework import permissions, viewsets
from rest_framework.response import Response

from chat.models import Chat, Message
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
        context = request.data.get("context", instance.context)

        # Update name if new context
        if instance.context != context:
            print(f"Found new context: {context}")
            summary = _build_summary(context)
            instance.name = summary
        instance.context = context

        # call the LLM model
        llm_result = call_llm(instance, message)
        Message.objects.create(chat=instance, role="user", parts=message)
        Message.objects.create(chat=instance, role="model", parts=llm_result)

        instance.save()

        return Response({"message_html": to_markdown(llm_result), "chat_name": instance.name})


def _build_summary(context):
    mes_history = [{"role": "user", "parts": [context]}]
    ctx = """
    The following message will be a context for an llm chatbot, 
    summarize the context into as few a words as possible so that we can create a title for the chat. 
    do not respond to the message, just summarize it into a title.
    do not respond with more than 5 words.
    """

    summary = run_llm(mes_history, ctx)
    return summary


def call_llm(instance, message):
    message_history = Message.objects.filter(chat=instance).order_by("-created_at")
    message_history = [{"role": message.role, "parts": [message.parts]} for message in message_history]
    context = instance.context
    message_history.append({"role": "user", "parts": [message]})

    llm_result = run_llm(message_history, context)
    return llm_result
