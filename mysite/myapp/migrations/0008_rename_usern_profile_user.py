# Generated by Django 4.2.1 on 2023-06-07 17:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0007_alter_profile_image"),
    ]

    operations = [
        migrations.RenameField(
            model_name="profile",
            old_name="usern",
            new_name="user",
        ),
    ]
