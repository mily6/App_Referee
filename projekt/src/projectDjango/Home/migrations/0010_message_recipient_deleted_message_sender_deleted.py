# Generated by Django 4.2.5 on 2023-09-20 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0009_alter_message_recipient'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='recipient_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='message',
            name='sender_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
