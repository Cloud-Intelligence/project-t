import json

from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.decorators import action

from chat.models import Chat, Message
from chat.serializers import ChatSerializer
from .utils import run_llm, to_markdown, count_tokens


class ChatViewSet(viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Chat.objects.all().order_by('-created_date')
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.all().order_by('-created_date')

    def update(self, request, *args, **kwargs):
        # TODO: Check current user or admin
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
        # TODO: need to save the token count to the message object
        llm_result, token_count = call_llm(instance, message)
        Message.objects.create(chat=instance, role="user", parts=message, tokens=token_count)
        Message.objects.create(chat=instance, role="model", parts=llm_result, tokens=token_count)

        instance.save()

        return Response({"message_html": to_markdown(llm_result), "chat_name": instance.name})

    @action(detail=True, methods=['DELETE'], url_path='delete-message/(?P<msg_id>[0-9]+)', url_name='delete-message')
    def delete_message(self, request, pk=None, msg_id=None):
        # TODO: Check current user or admin
        message = Message.objects.get(pk=msg_id)
        message.deleted = True
        message.save()
        return Response({"message": "Message deleted"})

    @action(detail=True, methods=['PUT'], url_path='star-message/(?P<msg_id>[0-9]+)', url_name='star-message')
    def star_message(self, request, pk=None, msg_id=None):
        # TODO: Check current user or admin
        print(f"Star message: {msg_id}, chat_id {pk}")
        message = Message.objects.get(pk=msg_id)
        message.starred = not message.starred
        message.save()
        return Response({"message": f"Message starred: {message.starred}"})


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
    message_history = [
        {"role": message.role, "parts": [message.parts], "pk": message.pk, "no_delete": message.no_delete}
        for message in message_history
    ]
    context = instance.context

    # todo: get size of tokens here and add to object
    user_message_token_count = count_tokens(message)
    message_history.append({"role": "user", "parts": [message], "tokens": user_message_token_count})

    # todo: get token size of result to add to object
    llm_result, token_count = run_llm(message_history, context)
    return llm_result, token_count
