# Generated by Django 3.0.3 on 2020-02-07 19:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_auto_20200206_1300"),
    ]

    operations = [
        migrations.RenameField(
            model_name="znosubject",
            old_name="subject_description",
            new_name="description",
        ),
        migrations.RenameField(
            model_name="znosubject", old_name="is_active_subject", new_name="is_active",
        ),
        migrations.RenameField(
            model_name="znosubject", old_name="subject_title", new_name="title",
        ),
        migrations.RemoveField(model_name="znosubject", name="subject_other",),
    ]
