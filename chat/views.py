import json
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Q, F


from .models import Chat, Message, SQLQuery
from .utils import to_markdown, count_tokens
from django.conf import settings


class ChatListView(LoginRequiredMixin, ListView):
    model = Chat
    template_name = "chat/list.html"
    context_object_name = "chats"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '') 
        return context

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            chat_vector = SearchVector('name', 'context')
            chat_query = SearchQuery(query)
            
            message_vector = SearchVector('message__parts')
            message_query = SearchQuery(query)
            
            return Chat.objects.annotate(
                rank=SearchRank(chat_vector, chat_query) + SearchRank(message_vector, message_query)
            ).filter(
                Q(rank__gte=0.001)
            ).order_by('-rank').distinct()
        return Chat.objects.filter(user=self.request.user).order_by('-created_date')


class create_chat(LoginRequiredMixin, View):
  def get(self, request):
    new_chat = Chat.objects.create(user=request.user, name="New Chat")
    return redirect('chat', pk=new_chat.pk)


class ChatDetailView(LoginRequiredMixin, DetailView):
  model = Chat
  template_name = "chat/chat.html"
  # TODO: Check current user or admin

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    history = Message.objects.filter(chat=context["chat"], deleted=False).order_by("created_at")
    history = [{"role": his.role, "parts": [his.parts], "pk": his.pk, "starred": his.starred, "tokens": his.tokens} for his in history]

    size_count_tokens = 0

    if history: 
      size_count_tokens = sum([his["tokens"] for his in history])

      for his in history:
        his["parts"] = to_markdown("\n\n".join([part for part in his.get("parts", [])]))

    context["chat"].history = history
    context["size_count"] = size_count_tokens
    context["size_count_percentage"] = (size_count_tokens/1000000)*100

    sql_queries = SQLQuery.objects.filter(chat=context["chat"]).order_by("-created_at")
    context["sql_queries"] = sql_queries

    return context
