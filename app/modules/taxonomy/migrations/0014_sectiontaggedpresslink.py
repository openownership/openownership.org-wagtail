# Generated by Django 3.2.12 on 2022-03-24 12:27

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0061_auto_20220321_1219'),
        ('taxonomy', '0013_auto_20220321_1219'),
    ]

    operations = [
        migrations.CreateModel(
            name='SectionTaggedPressLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_object', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='section_tagged', to='content.presslink')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='section_tag_press_links', to='taxonomy.sectiontag')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
