from django.db import models


# Create your models here.
class ZNOSubject(models.Model):
    title = models.CharField("Назва предмету", null=False, blank=False, max_length=50)
    description = models.TextField("Гасло", null=True, blank=True, max_length=1000)
    telegram_bot_name = models.CharField(
        "Telegram бот", null=True, blank=True, max_length=50
    )
    viber_bot_name = models.CharField("Viber бот", null=True, blank=True, max_length=50)
    messenger_bot_name = models.CharField(
        "Messenger бот", null=True, blank=True, max_length=50
    )
    image_title = models.CharField(
        "Зображення мініатюри", null=True, blank=True, max_length=50
    )
    image_top = models.CharField(
        "Основне зображення", null=True, blank=True, max_length=50
    )
    is_active = models.BooleanField("Активний", default=False)
    wide_thumbnail = models.BooleanField("Широка мініатюра", default=False)

    order = models.PositiveIntegerField("Порядок", default=0, blank=False, null=False)

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предмети"

        ordering = ["order"]

    def __str__(self):
        return f"Subject: {self.title}"
