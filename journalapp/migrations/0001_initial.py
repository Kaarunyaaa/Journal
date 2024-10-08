# Generated by Django 4.2.5 on 2024-09-11 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='entry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('isEdited', models.BooleanField(default=False)),
                ('edited_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
