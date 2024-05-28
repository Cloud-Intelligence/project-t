from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin



class HomePageView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, "homepage/homepage.html")
