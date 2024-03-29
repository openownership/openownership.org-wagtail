# Generated by Django 3.2.12 on 2022-03-11 10:05

from django.db import migrations
import modelcluster.contrib.taggit


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '0012_principletag_principletaggedpage'),
        ('content', '0055_auto_20220311_0953'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogarticlepage',
            name='principles',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taxonomy.PrincipleTaggedPage', to='taxonomy.PrincipleTag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='jobpage',
            name='principles',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taxonomy.PrincipleTaggedPage', to='taxonomy.PrincipleTag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='newsarticlepage',
            name='principles',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taxonomy.PrincipleTaggedPage', to='taxonomy.PrincipleTag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='publicationfrontpage',
            name='principles',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taxonomy.PrincipleTaggedPage', to='taxonomy.PrincipleTag', verbose_name='Tags'),
        ),
    ]
