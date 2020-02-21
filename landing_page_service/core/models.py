from django.db import models


# Create your models here.
class ZNOSubject(models.Model):
    title = models.CharField(null=False, blank=False, max_length=50)
    description = models.TextField(null=True, blank=True, max_length=1000)
    telegram_bot_name = models.CharField(null=True, blank=True, max_length=50)
    viber_bot_name = models.CharField(null=True, blank=True, max_length=50)
    messenger_bot_name = models.CharField(null=True, blank=True, max_length=50)
    image_title = models.CharField(null=True, blank=True, max_length=50)
    image_top = models.CharField(null=True, blank=True, max_length=50)
    is_active = models.BooleanField(default=False)

    # image_title = models.ImageField(null=True, blank=True, upload_to="images/")
    # image_top = models.ImageField(null=True, blank=True, upload_to="images/")

    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Subject: {self.title}"
