# Generated by Django 3.1.7 on 2021-09-13 13:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stockmgmt', '0002_stockhistory'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stockhistory',
            old_name='receive_by',
            new_name='received_by',
        ),
        migrations.RenameField(
            model_name='stockhistory',
            old_name='receive_quantity',
            new_name='received_quantity',
        ),
    ]
