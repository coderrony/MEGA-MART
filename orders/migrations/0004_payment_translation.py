# Generated by Django 4.1.7 on 2023-05-14 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_remove_orderproduct_variation_orderproduct_variation'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='translation',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
