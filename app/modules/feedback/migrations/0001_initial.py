# Generated by Django 4.1.7 on 2023-06-02 10:49

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailcore', '0083_workflowcontenttype'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedbackFormSubmission',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('why_option', models.CharField(max_length=150, null=True, verbose_name='Why')),
                ('where_option', models.CharField(max_length=150, null=True, verbose_name='Where')),
                ('why_other', models.TextField(null=True, verbose_name='Other reason')),
                ('where_other', models.TextField(null=True, verbose_name='Other reason')),
                ('created_at', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True)),
                ('updated_at', django_extensions.db.fields.ModificationDateTimeField(auto_now=True)),
                ('page', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='feedback', to='wagtailcore.page')),
            ],
            options={
                'verbose_name_plural': 'Feedback',
                'ordering': ['-created_at'],
            },
        ),
    ]
