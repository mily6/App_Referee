# Generated by Django 4.2.5 on 2023-10-12 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0012_rename_nazwa_team_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referee',
            name='class_referee',
            field=models.CharField(choices=[('IV LIGA', 'IV LIGA'), ('Klasa Okręgowa', 'Klasa Okręgowa'), ('A Klasa', 'A Klasa'), ('B Klasa', 'B Klasa'), ('Pozostali', 'Pozostali')], default='B Klasa', max_length=100),
        ),
    ]
