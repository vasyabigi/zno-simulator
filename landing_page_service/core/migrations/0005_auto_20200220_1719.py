# Generated by Django 3.0.3 on 2020-02-20 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_znosubject_image_title"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="znosubject", options={"ordering": ["order"]},
        ),
        migrations.RemoveField(model_name="znosubject", name="whatsapp_bot_name",),
        migrations.AddField(
            model_name="znosubject",
            name="order",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
