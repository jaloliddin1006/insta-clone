# Generated by Django 4.2.7 on 2023-11-19 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='content',
            field=models.TextField(null=True),
        ),
    ]
