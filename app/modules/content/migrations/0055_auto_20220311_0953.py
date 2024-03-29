# Generated by Django 3.2.12 on 2022-03-11 09:53

from django.db import migrations
import modelcluster.contrib.taggit


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '0011_sectiontag_sectiontaggedpage'),
        ('content', '0054_publicationsindexpage'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogarticlepage',
            name='sections',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taxonomy.SectionTaggedPage', to='taxonomy.SectionTag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='jobpage',
            name='sections',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taxonomy.SectionTaggedPage', to='taxonomy.SectionTag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='newsarticlepage',
            name='sections',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taxonomy.SectionTaggedPage', to='taxonomy.SectionTag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='publicationfrontpage',
            name='sections',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taxonomy.SectionTaggedPage', to='taxonomy.SectionTag', verbose_name='Tags'),
        ),
    ]
