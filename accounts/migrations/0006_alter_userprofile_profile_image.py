# Generated by Django 4.1.7 on 2023-05-27 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_userprofile_profile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profile_image',
            field=models.ImageField(blank=True, default='default_img.png', null=True, upload_to='profile_image/'),
        ),
    ]
