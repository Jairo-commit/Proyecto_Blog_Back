# Generated by Django 5.1.6 on 2025-03-13 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_alter_blogpost_author_access_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='excerpt',
            field=models.TextField(default='No Excerpt'),
        ),
    ]
