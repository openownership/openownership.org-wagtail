# Generated by Django 3.0.9 on 2020-08-05 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ViewCount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page_id', models.IntegerField()),
                ('date', models.DateField()),
                ('count', models.IntegerField(default=0)),
            ],
            options={
                'unique_together': {('page_id', 'date')},
            },
        ),
    ]
