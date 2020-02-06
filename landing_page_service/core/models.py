from django.db import models


# Create your models here.
class ZNOSubject(models.Model):
    subject_title = models.CharField(max_length=50)
    subject_description = models.TextField(max_length=1000,)
    telegram_bot_name = models.CharField(max_length=50, default="")
    viber_bot_name = models.CharField(max_length=50, default="")
    messenger_bot_name = models.CharField(max_length=50, default="")
    whatsapp_bot_name = models.CharField(max_length=50, default="")
    is_active_subject = models.BooleanField(default=False)
    subject_other = models.TextField(max_length=1000, default="")

    def __str__(self):
        return f"Subject: {self.subject_title}"
