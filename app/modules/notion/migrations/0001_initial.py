# Generated by Django 3.1.14 on 2022-02-22 10:40

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import modules.content.blocks.stream
import wagtail.contrib.table_block.blocks
import wagtail.blocks
import wagtail.fields
import wagtail.documents.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailcore', '0060_fix_workflow_unique_constraint'),
    ]

    operations = [
        migrations.CreateModel(
            name='CountryTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='name')),
                ('slug', models.SlugField(max_length=100, unique=True, verbose_name='slug')),
                ('body', wagtail.fields.StreamField([('rich_text', wagtail.blocks.RichTextBlock(features=['h2', 'h3', 'h4', 'h5', 'h6', 'bold', 'italic', 'small', 'ol', 'ul', 'link', 'document-link'])), ('embed', modules.content.blocks.stream.EmbedBlock()), ('table', wagtail.contrib.table_block.blocks.TableBlock()), ('pull_quote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.TextBlock(required=True))])), ('block_quote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.TextBlock(required=True))])), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True))])), ('cta_block_form', wagtail.blocks.StructBlock([('link_type', wagtail.blocks.ChoiceBlock(choices=[('none', 'None'), ('page', 'Page'), ('document', 'Document'), ('url', 'URL')])), ('link_page', wagtail.blocks.PageChooserBlock(label='Linked Page', required=False)), ('link_document', wagtail.documents.blocks.DocumentChooserBlock(label='Linked Document', required=False)), ('link_url', wagtail.blocks.CharBlock(label='URL', required=False)), ('link_label', wagtail.blocks.CharBlock(help_text="If blank will display 'Find out more'", required=False))]))], blank=True)),
                ('notion_id', models.CharField(max_length=255, unique=True, verbose_name='Notion ID')),
                ('notion_created', models.DateTimeField(blank=True, null=True, verbose_name='Notion Created')),
                ('notion_updated', models.DateTimeField(blank=True, null=True, verbose_name='Notion Updated')),
                ('archived', models.BooleanField(blank=True, null=True, verbose_name='Archived')),
                ('icon', models.CharField(blank=True, max_length=25, null=True, verbose_name='Icon')),
                ('oo_support', models.CharField(blank=True, max_length=255, null=True, verbose_name='OO Support')),
            ],
            options={
                'verbose_name': 'Country',
                'verbose_name_plural': 'Countries',
            },
        ),
        migrations.CreateModel(
            name='DisclosureRegime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notion_id', models.CharField(max_length=255, unique=True, verbose_name='Notion ID')),
                ('notion_created', models.DateTimeField(blank=True, null=True, verbose_name='Notion Created')),
                ('notion_updated', models.DateTimeField(blank=True, null=True, verbose_name='Notion Updated')),
                ('archived', models.BooleanField(blank=True, null=True, verbose_name='Archived')),
                ('title', models.CharField(blank=True, max_length=255, null=True, verbose_name='Title')),
                ('coverage', models.CharField(blank=True, max_length=255, null=True, verbose_name='Coverage')),
                ('on_oo_register', models.BooleanField(default=False, verbose_name='On OO Register')),
                ('r_central', models.CharField(blank=True, max_length=255, null=True, verbose_name='Central register (R-CENTRAL)')),
                ('public_access', models.CharField(blank=True, max_length=255, null=True, verbose_name='Public Access')),
                ('bulk_data', models.CharField(blank=True, max_length=255, null=True, verbose_name='Bulk Data')),
                ('r_api', models.CharField(blank=True, max_length=255, null=True, verbose_name='API (R-API)')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='disclosure_regimes', to='notion.countrytag', to_field='notion_id')),
            ],
            options={
                'verbose_name': 'Disclosure Regime',
                'verbose_name_plural': 'Disclosure Regimes',
            },
        ),
        migrations.CreateModel(
            name='CountryTaggedPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_object', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='country_related_items', to='wagtailcore.page')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='country_related_pages', to='notion.countrytag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Commitment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notion_id', models.CharField(max_length=255, unique=True, verbose_name='Notion ID')),
                ('notion_created', models.DateTimeField(blank=True, null=True, verbose_name='Notion Created')),
                ('notion_updated', models.DateTimeField(blank=True, null=True, verbose_name='Notion Updated')),
                ('archived', models.BooleanField(blank=True, null=True, verbose_name='Archived')),
                ('date', models.DateField(blank=True, null=True, verbose_name='Date')),
                ('link', models.URLField(blank=True, null=True, verbose_name='Link')),
                ('commitment_type_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Commitment Type')),
                ('central_register', models.BooleanField(default=False, verbose_name='Central Register')),
                ('public_register', models.BooleanField(default=False, verbose_name='Public Register')),
                ('summary_text', wagtail.fields.RichTextField(blank=True, null=True, verbose_name='Summary Text')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commitments', to='notion.countrytag', to_field='notion_id')),
            ],
            options={
                'verbose_name': 'Commitment',
                'verbose_name_plural': 'Commitments',
            },
        ),
    ]
