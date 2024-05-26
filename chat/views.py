import json
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.shortcuts import redirect

from .models import Chat, Message
from .utils import to_markdown, count_tokens
from django.conf import settings


class ChatListView(ListView):
  model = Chat
  template_name = "chat/list.html"
  context_object_name = "chats"

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["algolia_app_code"]=settings.ALGOLIA["APPLICATION_ID"]
    context["algolia_ui"]=settings.ALGOLIA["ALGOLIA_UI"]
    return context

  def get_queryset(self):
    return Chat.objects.filter(user=self.request.user).order_by('-created_date')


class create_chat(View):
  def get(self, request):
    new_chat = Chat.objects.create(user=request.user, name="New Chat")
    return redirect('chat', pk=new_chat.pk)


class ChatDetailView(DetailView):
  model = Chat
  template_name = "chat/chat.html"

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    history = Message.objects.filter(chat=context["chat"]).order_by("-created_at")
    history = [{"role": his.role, "parts": [his.parts]} for his in history]
   
    size_count_tokens = 0

    if history: 
      size_count_tokens = count_tokens(history)

      for his in history:
        his["parts"] = to_markdown("\n\n".join([part for part in his.get("parts", [])]))

    context["chat"].history = history
    context["size_count"] = size_count_tokens
    context["size_count_percentage"] = (size_count_tokens/1000000)*100

    return context
