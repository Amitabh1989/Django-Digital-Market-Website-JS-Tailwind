# Generated by Django 4.2.1 on 2023-06-07 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0006_rename_user_profile_usern"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="image",
            field=models.ImageField(
                default="profile/profilepic.gif", upload_to="profile"
            ),
        ),
    ]