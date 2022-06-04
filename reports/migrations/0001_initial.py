# Generated by Django 4.0.1 on 2022-01-30 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_time', models.DateTimeField(auto_now_add=True)),
                ('log_type', models.CharField(max_length=50)),
                ('log_message', models.TextField()),
            ],
        ),
    ]
