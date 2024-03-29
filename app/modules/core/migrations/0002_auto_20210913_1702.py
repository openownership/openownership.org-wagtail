# Generated by Django 3.1.13 on 2021-09-13 16:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers
import wagtail.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        ('wagtailcore', '0060_fix_workflow_unique_constraint'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taggit', '0003_taggeditem_add_unique_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteimage',
            name='uploaded_by_user',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='uploaded by user'),
        ),
        migrations.AddField(
            model_name='sitedocument',
            name='collection',
            field=models.ForeignKey(default=wagtail.models.get_root_collection_id, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtailcore.collection', verbose_name='collection'),
        ),
        migrations.AddField(
            model_name='sitedocument',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text=None, through='taggit.TaggedItem', to='taggit.Tag', verbose_name='tags'),
        ),
        migrations.AddField(
            model_name='sitedocument',
            name='uploaded_by_user',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='uploaded by user'),
        ),
        migrations.AddField(
            model_name='navigationsettings',
            name='site',
            field=models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to='wagtailcore.site'),
        ),
        migrations.AddField(
            model_name='metatagsettings',
            name='image',
            field=models.ForeignKey(blank=True, help_text='A default image to use when shared on Facebook (aim for 1200x630)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.siteimage'),
        ),
        migrations.AddField(
            model_name='metatagsettings',
            name='site',
            field=models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to='wagtailcore.site'),
        ),
        migrations.AddField(
            model_name='documentdownload',
            name='document',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_downloads', to='core.sitedocument'),
        ),
        migrations.AddField(
            model_name='documentdownload',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='document_downloads', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='analyticssettings',
            name='site',
            field=models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to='wagtailcore.site'),
        ),
        migrations.AlterUniqueTogether(
            name='siteimagerendition',
            unique_together={('image', 'filter_spec', 'focal_point_key')},
        ),
    ]
