# Generated by Django 5.1.2 on 2025-02-14 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utakais', '0006_alter_event_eisou_doc_alter_event_eisou_pdf_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='message',
            field=models.TextField(default='', max_length=200, verbose_name='備考欄'),
        ),
    ]
