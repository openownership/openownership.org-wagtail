# Generated by Django 3.1.14 on 2022-02-03 12:16

from django.db import migrations, models
import django.db.models.deletion
import wagtail.fields
import wagtailcache.cache


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailredirects', '0006_redirect_increase_max_length'),
        ('core', '0002_auto_20210913_1702'),
        ('wagtailsearchpromotions', '0002_capitalizeverbose'),
        ('wagtailforms', '0004_add_verbose_name_plural'),
        ('wagtailcore', '0060_fix_workflow_unique_constraint'),
        ('content', '0003_auto_20220202_1705'),
    ]

    operations = [
        migrations.CreateModel(
            name='SectionPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('hero_headline', wagtail.fields.RichTextField(blank=True, null=True, verbose_name='Headline')),
                ('hero_body', wagtail.fields.RichTextField(blank=True, null=True, verbose_name='Body text')),
                ('blurb', models.TextField(blank=True, null=True)),
                ('display_date', models.DateField(blank=True, help_text='If blank, this will be set to the date the page was first published', null=True)),
                ('body', wagtail.fields.StreamField([], blank=True)),
                ('thumbnail', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.siteimage')),
            ],
            options={
                'verbose_name': 'Section page',
            },
            bases=(wagtailcache.cache.WagtailCacheMixin, 'wagtailcore.page', models.Model),
        ),
        migrations.CreateModel(
            name='IndexSectionPage',
            fields=[
                ('sectionpage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='content.sectionpage')),
            ],
            options={
                'abstract': False,
            },
            bases=('content.sectionpage',),
        ),
        migrations.DeleteModel(
            name='LandingPage',
        ),
    ]
