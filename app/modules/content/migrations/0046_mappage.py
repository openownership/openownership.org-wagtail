# Generated by Django 3.2.12 on 2022-03-03 10:36

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.fields
import wagtailcache.cache


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0066_collection_management_permissions'),
        ('core', '0003_auto_20220216_1611'),
        ('content', '0045_auto_20220301_1824'),
    ]

    operations = [
        migrations.CreateModel(
            name='MapPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('blurb', models.TextField(blank=True, null=True)),
                ('display_date', models.DateField(blank=True, help_text='If blank, this will be set to the date the page was first published', null=True)),
                ('intro', wagtail.core.fields.RichTextField(blank=True, null=True)),
                ('thumbnail', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.siteimage')),
            ],
            options={
                'abstract': False,
            },
            bases=(wagtailcache.cache.WagtailCacheMixin, 'wagtailcore.page'),
        ),
    ]