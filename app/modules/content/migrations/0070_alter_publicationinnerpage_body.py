# Generated by Django 4.1.7 on 2023-06-29 09:28

from django.db import migrations
import modules.content.blocks.stream
import wagtail.blocks
import wagtail.contrib.table_block.blocks
import wagtail.documents.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0069_taxonomypage_body_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publicationinnerpage',
            name='body',
            field=wagtail.fields.StreamField([('rich_text', wagtail.blocks.RichTextBlock(features=['h2', 'h3', 'h4', 'h5', 'h6', 'bold', 'italic', 'small', 'ol', 'ul', 'link', 'document-link'])), ('embed', modules.content.blocks.stream.EmbedBlock()), ('table', wagtail.contrib.table_block.blocks.TableBlock()), ('pull_quote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.TextBlock(required=True))])), ('summary_box', wagtail.blocks.StructBlock([('text', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'small', 'ol', 'ul', 'link', 'document-link'], required=True))])), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True))])), ('cta_block_form', wagtail.blocks.StructBlock([('link_type', wagtail.blocks.ChoiceBlock(choices=[('none', 'None'), ('page', 'Page'), ('document', 'Document'), ('url', 'URL')])), ('link_page', wagtail.blocks.PageChooserBlock(label='Linked Page', required=False)), ('link_document', wagtail.documents.blocks.DocumentChooserBlock(label='Linked Document', required=False)), ('link_url', wagtail.blocks.CharBlock(label='URL', required=False)), ('link_label', wagtail.blocks.CharBlock(help_text="If blank will display 'Find out more'", required=False))])), ('disclosure', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=True)), ('body', wagtail.blocks.StreamBlock([('rich_text', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'small', 'ol', 'ul', 'link', 'document-link'])), ('embed', modules.content.blocks.stream.EmbedBlock()), ('table', wagtail.contrib.table_block.blocks.TableBlock()), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True))]))], max_num=1))])), ('raw_html', wagtail.blocks.RawHTMLBlock(label='Raw HTML')), ('footnote', wagtail.blocks.StructBlock([('anchor', wagtail.blocks.CharBlock(help_text='This is the anchor that you link to in your RichText.\n            Try to make it URL-safe, using `-` characters instead of spaces and punctuation\n            characters.', max_length=50)), ('body', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'underline', 'small', 'link'], help_text='Body for the footnote. Wherever you place this block in the stream, it\n            will render at the foot of the page.', required=False))]))], blank=True, use_json_field=True),
        ),
    ]