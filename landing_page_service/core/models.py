from django.db import models
from adminsortable.models import SortableMixin


class ZNOSubject(models.Model):

    title = models.CharField(max_length=50)
    description = models.TextField(max_length=1000, null=False, blank=True)
    telegram_bot_name = models.CharField(max_length=50, null=False, blank=True)
    viber_bot_name = models.CharField(max_length=50, null=False, blank=True)
    messenger_bot_name = models.CharField(max_length=50, null=False, blank=True)
    whatsapp_bot_name = models.CharField(max_length=50, null=False, blank=True)
    is_active = models.BooleanField(default=False)
    image = models.ImageField(upload_to="static/img/", blank=True)

    title_order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ["title_order"]

    def __str__(self):
        return f"Subject: {self.title}"
