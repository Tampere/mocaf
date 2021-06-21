# Generated by Django 3.1.9 on 2021-06-20 20:26

from django.db import migrations, models


def migrate_notification_templates(apps, schema_editor):
    NotificationTemplate = apps.get_model('notifications', 'NotificationTemplate')
    NotificationTemplate.objects.filter(event_type='monthly_summary').update(event_type='monthly_summary_bronze')


def migrate_notification_templates_reverse(apps, schema_editor):
    NotificationTemplate = apps.get_model('notifications', 'NotificationTemplate')
    NotificationTemplate.objects.filter(event_type='monthly_summary_bronze').update(event_type='monthly_summary')


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationtemplate',
            name='event_type',
            field=models.CharField(choices=[('monthly_summary_gold', 'Monthly summary (gold-level budget)'), ('monthly_summary_silver', 'Monthly summary (silver-level budget)'), ('monthly_summary_bronze', 'Monthly summary (bronze-level budget or worse)'), ('welcome_message', 'Welcome message'), ('no_recent_trips', 'No recent trips')], max_length=22),
        ),
        migrations.RunPython(migrate_notification_templates, migrate_notification_templates_reverse),
    ]
