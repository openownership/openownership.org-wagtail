# Generated by Django 3.1.14 on 2022-02-15 13:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '0001_create_publication_type'),
        ('content', '0026_remove_publicationinnerpage_sort_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogarticlepage',
            name='publication_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pages_blogarticlepage', to='taxonomy.publicationtype'),
        ),
        migrations.AddField(
            model_name='jobpage',
            name='publication_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pages_jobpage', to='taxonomy.publicationtype'),
        ),
        migrations.AddField(
            model_name='newsarticlepage',
            name='publication_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pages_newsarticlepage', to='taxonomy.publicationtype'),
        ),
        migrations.AddField(
            model_name='publicationfrontpage',
            name='publication_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pages_publicationfrontpage', to='taxonomy.publicationtype'),
        ),
    ]
