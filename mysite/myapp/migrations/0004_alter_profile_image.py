# Generated by Django 4.2.1 on 2023-06-07 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0003_profile"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="image",
            field=models.ImageField(
                default="https://media.tenor.com/ir2nX96xSJUAAAAC/ghosts-my-profile.gif",
                upload_to="profile",
            ),
        ),
    ]
