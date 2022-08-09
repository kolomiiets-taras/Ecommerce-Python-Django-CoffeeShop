# Generated by Django 4.0.5 on 2022-07-19 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0006_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipping',
            name='payment',
            field=models.CharField(choices=[('Оплата при отриманні', 'Оплата при отриманні'), ('Оплата на картку', 'Оплата на картку')], default='Оплата при отриманні', max_length=200),
        ),
    ]
