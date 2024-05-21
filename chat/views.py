import json
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.shortcuts import redirect

from .models import Chat
from .utils import to_markdown


class ChatListView(ListView):
  model = Chat
  template_name = "chat/list.html"
  context_object_name = "chats"  # Optional customization
  #
  # def get_queryset(self):  # Optional to filter or modify queryset
  #   return Chat.objects.all().order_by('-created_date')

class create_chat(View):
  def get(self, request):
    new_chat = Chat.objects.create()
    # redirect to details page
    return redirect('chat', pk=new_chat.pk)
    # return redirect(ChatDetailView, pk=new_chat.pk)

class ChatDetailView(DetailView):
  model = Chat
  template_name = "chat/chat.html"

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    history = context["chat"].history
    # print(history)
    if history:
      history = json.loads(history)
      for his in history:
        his["parts"] = "<br>".join([to_markdown(part) for part in his.get("parts", [])])

    print(history)
    context["chat"].history = history
    return context

#
# class ChatView(View):
#     def list(self, request):
#         return render(request, "chat/list.html")
#
#     def get(self, request, pk=None):
#         print("loading chat view with pk: ", pk)
#         return render(request, "chat/chat.html", {"chat_id": pk})
