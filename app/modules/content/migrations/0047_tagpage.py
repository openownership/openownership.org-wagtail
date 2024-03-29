# Generated by Django 3.2.12 on 2022-03-03 09:47

from django.db import migrations, models
import django.db.models.deletion
import wagtail.fields
import wagtailcache.cache


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '0009_auto_20220301_1824'),
        ('core', '0003_auto_20220216_1611'),
        ('wagtailcore', '0066_collection_management_permissions'),
        ('content', '0046_taxonomypage'),
    ]

    operations = [
        migrations.CreateModel(
            name='TagPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('blurb', models.TextField(blank=True, null=True)),
                ('display_date', models.DateField(blank=True, help_text='If blank, this will be set to the date the page was first published', null=True)),
                ('intro', wagtail.fields.RichTextField(blank=True, null=True)),
                ('focus_area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tagpages', to='taxonomy.focusareatag')),
                ('publication_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tagpages', to='taxonomy.publicationtype')),
                ('sector', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tagpages', to='taxonomy.sectortag')),
                ('thumbnail', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.siteimage')),
            ],
            options={
                'abstract': False,
            },
            bases=(wagtailcache.cache.WagtailCacheMixin, 'wagtailcore.page'),
        ),
    ]
