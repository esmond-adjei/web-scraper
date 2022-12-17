# Generated by Django 4.1 on 2022-12-04 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_user_moviedata_username'),
    ]

    operations = [
        migrations.RenameField(
            model_name='moviedata',
            old_name='movie',
            new_name='moviename',
        ),
        migrations.AlterField(
            model_name='moviedata',
            name='imagelink',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
    ]
