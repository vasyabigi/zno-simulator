from django.db import models


# Create your models here.
class ZNOSubject(models.Model):
    title = models.CharField(null=False, blank=False, max_length=50)
    description = models.TextField(null=True, blank=True, max_length=1000)
    telegram_bot_name = models.CharField(null=True, blank=True, max_length=50)
    viber_bot_name = models.CharField(null=True, blank=True, max_length=50)
    messenger_bot_name = models.CharField(null=True, blank=True, max_length=50)
    whatsapp_bot_name = models.CharField(null=True, blank=True, max_length=50)
    image_title = models.CharField(null=True, blank=True, max_length=50)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"Subject: {self.title}"
