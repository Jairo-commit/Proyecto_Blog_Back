# Generated by Django 5.1.6 on 2025-03-10 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blogpost',
            old_name='Authenticated',
            new_name='authenticated_access',
        ),
        migrations.RenameField(
            model_name='blogpost',
            old_name='Team',
            new_name='group_access',
        ),
        migrations.RenameField(
            model_name='blogpost',
            old_name='Public',
            new_name='public_access',
        ),
        migrations.RemoveField(
            model_name='blogpost',
            name='Author',
        ),
        migrations.AddField(
            model_name='blogpost',
            name='author_access',
            field=models.CharField(choices=[('None', 'None'), ('Read', 'Read'), ('Read and Edit', 'Read and Edit')], default='Read and Edit', max_length=15),
        ),
    ]
