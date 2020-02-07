from django.contrib import admin
from .models import ZNOSubject

# Register your models here.
@admin.register(ZNOSubject)
class ZNOSubjectModel(admin.ModelAdmin):
    list_display = (
        "title",
        "description",
        "telegram_bot_name",
        "viber_bot_name",
        "messenger_bot_name",
        "whatsapp_bot_name",
        "is_active",
    )
    list_editable = ("is_active",)
    sortable = "title"
