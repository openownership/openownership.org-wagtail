# Generated by Django 4.2.4 on 2023-11-30 12:53

from django.db import migrations, models
import modules.content.blocks.stream
import wagtail.blocks
import wagtail.contrib.table_block.blocks
import wagtail.documents.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('notion', '0023_region_blurb'),
    ]

    operations = [
        migrations.AlterField(
            model_name='countrytag',
            name='body',
            field=wagtail.fields.StreamField([('rich_text', wagtail.blocks.RichTextBlock(features=['h2', 'h3', 'h4', 'h5', 'h6', 'bold', 'italic', 'small', 'ol', 'ul', 'link', 'document-link'])), ('embed', modules.content.blocks.stream.EmbedBlock()), ('table', wagtail.contrib.table_block.blocks.TableBlock()), ('pull_quote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.TextBlock(required=True))])), ('summary_box', wagtail.blocks.StructBlock([('text', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'small', 'ol', 'ul', 'link', 'document-link'], required=True))])), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True))])), ('cta_block_form', wagtail.blocks.StructBlock([('link_type', wagtail.blocks.ChoiceBlock(choices=[('none', 'None'), ('page', 'Page'), ('document', 'Document'), ('url', 'URL')])), ('link_page', wagtail.blocks.PageChooserBlock(label='Linked Page', required=False)), ('link_document', wagtail.documents.blocks.DocumentChooserBlock(label='Linked Document', required=False)), ('link_url', wagtail.blocks.CharBlock(label='URL', required=False)), ('link_label', wagtail.blocks.CharBlock(help_text="If blank will display 'Find out more'", required=False))])), ('disclosure', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=True)), ('body', wagtail.blocks.StreamBlock([('rich_text', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'small', 'ol', 'ul', 'link', 'document-link'])), ('embed', modules.content.blocks.stream.EmbedBlock()), ('table', wagtail.contrib.table_block.blocks.TableBlock()), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True))]))], max_num=1))])), ('raw_html', wagtail.blocks.RawHTMLBlock(label='Raw HTML', template='blocks/raw_html.jinja'))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='countrytag',
            name='icon',
            field=models.CharField(blank=True, default='', max_length=25, verbose_name='Icon'),
        ),
        migrations.AlterField(
            model_name='countrytag',
            name='iso2',
            field=models.CharField(blank=True, default='', max_length=10, verbose_name='ISO2'),
        ),
        migrations.AlterField(
            model_name='countrytag',
            name='oo_ongoing_work_title',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Open Ownership Ongoing Work Title'),
        ),
        migrations.AlterField(
            model_name='countrytag',
            name='oo_support',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='OO Support'),
        ),
        migrations.AlterField(
            model_name='disclosureregime',
            name='api_available',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='API available'),
        ),
        migrations.AlterField(
            model_name='disclosureregime',
            name='central_register',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Central Register'),
        ),
        migrations.AlterField(
            model_name='disclosureregime',
            name='coverage_legislation_url',
            field=models.TextField(blank=True, default='', max_length=10000, verbose_name='Coverage: Legislation URL'),
        ),
        migrations.AlterField(
            model_name='disclosureregime',
            name='data_in_bods',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Data published in BODS'),
        ),
        migrations.AlterField(
            model_name='disclosureregime',
            name='definition_legislation_url',
            field=models.TextField(blank=True, default='', max_length=10000, verbose_name='Definition: Legislation URL'),
        ),
        migrations.AlterField(
            model_name='disclosureregime',
            name='legislation_url',
            field=models.TextField(blank=True, default='', max_length=10000, verbose_name='Legislation URL'),
        ),
        migrations.AlterField(
            model_name='disclosureregime',
            name='public_access',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Public Access'),
        ),
        migrations.AlterField(
            model_name='disclosureregime',
            name='public_access_legal_basis_url',
            field=models.TextField(blank=True, default='', max_length=10000, verbose_name='Public access: Legal basis URL'),
        ),
        migrations.AlterField(
            model_name='disclosureregime',
            name='public_access_protection_regime_url',
            field=models.TextField(blank=True, default='', max_length=10000, verbose_name='Public access: Protection regime URL'),
        ),
        migrations.AlterField(
            model_name='disclosureregime',
            name='public_access_register_url',
            field=models.URLField(blank=True, default='', max_length=1000, verbose_name='Public Access Register URL'),
        ),
        migrations.AlterField(
            model_name='disclosureregime',
            name='sanctions_enforcement_legislation_url',
            field=models.TextField(blank=True, default='', max_length=10000, verbose_name='Public access: Legal basis URL'),
        ),
        migrations.AlterField(
            model_name='disclosureregime',
            name='stage',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Stage'),
        ),
        migrations.AlterField(
            model_name='disclosureregime',
            name='structured_data',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Structured data'),
        ),
        migrations.AlterField(
            model_name='disclosureregime',
            name='sufficient_detail_legislation_url',
            field=models.TextField(blank=True, default='', max_length=10000, verbose_name='Sufficient detail: Legislation URL'),
        ),
        migrations.AlterField(
            model_name='disclosureregime',
            name='threshold',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Threshold'),
        ),
        migrations.AlterField(
            model_name='disclosureregime',
            name='title',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='disclosureregime',
            name='year_launched',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Year Launched'),
        ),
    ]
