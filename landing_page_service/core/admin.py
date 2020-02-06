from django.contrib import admin
from .models import ZNOSubject

# Register your models here.
@admin.register(ZNOSubject)
class ZNOSubjectModel(admin.ModelAdmin):
    list_display = (
        "subject_title",
        "subject_description",
        "telegram_bot_name",
        "viber_bot_name",
        "messenger_bot_name",
        "whatsapp_bot_name",
        "is_active_subject",
        "subject_other",
    )
    list_editable = ("is_active_subject",)
    sortable = "subject_title"
