# Generated by Django 3.1.14 on 2022-02-09 18:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0021_teampage_teamprofilepage'),
    ]

    operations = [
        migrations.AddField(
            model_name='teamprofilepage',
            name='authorship',
            field=models.OneToOneField(blank=True, help_text='Link team member to their authorship of articles on the site', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='team_profile', to='content.author'),
        ),
    ]
