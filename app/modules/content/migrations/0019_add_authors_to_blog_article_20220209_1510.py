# Generated by Django 3.1.14 on 2022-02-09 15:10

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0018_auto_20220209_1427'),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AlterModelOptions(
            name='blogarticlepage',
            options={'verbose_name': 'Blog post page'},
        ),
        migrations.CreateModel(
            name='BlogArticleAuthorRelationship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_articles', to='content.author')),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='author_relationships', to='content.blogarticlepage')),
            ],
            options={
                'verbose_name': 'Post author',
                'verbose_name_plural': 'Post authors',
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]