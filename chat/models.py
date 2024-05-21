from django.db import models


class Chat(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    history = models.TextField(null=True, blank=True)
    context = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.history[:1]
