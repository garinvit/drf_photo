# Generated by Django 3.1 on 2021-12-16 14:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0003_auto_20211216_1602'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='album',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='photo.album'),
            preserve_default=False,
        ),
    ]
