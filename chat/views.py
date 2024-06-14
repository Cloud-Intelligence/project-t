import json
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, SearchHeadline
from django.db.models import Q

from .models import Chat, Message
from .utils import to_markdown, count_tokens
from django.conf import settings


class ChatListView(LoginRequiredMixin, ListView):
    model = Chat
    template_name = "chat/list.html"
    context_object_name = "chats"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        context['search_query'] = query

        if query:
            search_query = SearchQuery(query)
            vector = SearchVector('name', 'context')

            chats = Chat.objects.annotate(
                rank=SearchRank(vector, search_query),
                headline_name=SearchHeadline('name', search_query, start_sel='<mark>', stop_sel='</mark>'),
                headline_context=SearchHeadline('context', search_query, start_sel='<mark>', stop_sel='</mark>')
            ).filter(
                Q(rank__gte=0.001) | Q(message__parts__icontains=query)
            ).order_by('-rank').distinct()

            messages = Message.objects.filter(
                Q(parts__icontains=query),
                Q(chat__user=self.request.user)
            ).select_related('chat').annotate(
                headline_parts=SearchHeadline('parts', search_query, start_sel='<mark>', stop_sel='</mark>')
            ).distinct()

            context['chats'] = chats
            context['messages'] = messages
        else:
            context['chats'] = self.get_queryset()

        return context

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            vector = SearchVector('name', 'context') + SearchVector('message__parts')
            search_query = SearchQuery(query)
            return Chat.objects.annotate(
                rank=SearchRank(vector, search_query)
            ).filter(
                rank__gte=0.001,
                user=self.request.user
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

    return context
