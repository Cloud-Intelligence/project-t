# Generated by Django 4.2.4 on 2024-05-29 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0007_message_created_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="deleted",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="message",
            name="starred",
            field=models.BooleanField(default=False),
        ),
    ]