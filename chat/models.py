from django.db import models
from django.contrib.auth.models import User

class Chat(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    history = models.TextField(null=True, blank=True)
    context = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name or str(self.created_date)
