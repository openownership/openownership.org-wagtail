# Generated by Django 3.2.12 on 2022-03-01 11:43

from django.db import migrations
import modules.content.blocks.stream
import wagtail.contrib.table_block.blocks
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.documents.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '0006_add_blurb_and_body_to_publication_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='focusareatag',
            name='body',
            field=wagtail.core.fields.StreamField([('rich_text', wagtail.core.blocks.RichTextBlock(features=['h2', 'h3', 'h4', 'h5', 'h6', 'bold', 'italic', 'small', 'ol', 'ul', 'link', 'document-link'])), ('embed', modules.content.blocks.stream.EmbedBlock()), ('table', wagtail.contrib.table_block.blocks.TableBlock()), ('pull_quote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.TextBlock(required=True))])), ('summary_box', wagtail.core.blocks.StructBlock([('text', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'small', 'ol', 'ul', 'link', 'document-link'], required=True))])), ('image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True))])), ('cta_block_form', wagtail.core.blocks.StructBlock([('link_type', wagtail.core.blocks.ChoiceBlock(choices=[('none', 'None'), ('page', 'Page'), ('document', 'Document'), ('url', 'URL')])), ('link_page', wagtail.core.blocks.PageChooserBlock(label='Linked Page', required=False)), ('link_document', wagtail.documents.blocks.DocumentChooserBlock(label='Linked Document', required=False)), ('link_url', wagtail.core.blocks.CharBlock(label='URL', required=False)), ('link_label', wagtail.core.blocks.CharBlock(help_text="If blank will display 'Find out more'", required=False))]))], blank=True),
        ),
        migrations.AlterField(
            model_name='publicationtype',
            name='body',
            field=wagtail.core.fields.StreamField([('rich_text', wagtail.core.blocks.RichTextBlock(features=['h2', 'h3', 'h4', 'h5', 'h6', 'bold', 'italic', 'small', 'ol', 'ul', 'link', 'document-link'])), ('embed', modules.content.blocks.stream.EmbedBlock()), ('table', wagtail.contrib.table_block.blocks.TableBlock()), ('pull_quote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.TextBlock(required=True))])), ('summary_box', wagtail.core.blocks.StructBlock([('text', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'small', 'ol', 'ul', 'link', 'document-link'], required=True))])), ('image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True))])), ('cta_block_form', wagtail.core.blocks.StructBlock([('link_type', wagtail.core.blocks.ChoiceBlock(choices=[('none', 'None'), ('page', 'Page'), ('document', 'Document'), ('url', 'URL')])), ('link_page', wagtail.core.blocks.PageChooserBlock(label='Linked Page', required=False)), ('link_document', wagtail.documents.blocks.DocumentChooserBlock(label='Linked Document', required=False)), ('link_url', wagtail.core.blocks.CharBlock(label='URL', required=False)), ('link_label', wagtail.core.blocks.CharBlock(help_text="If blank will display 'Find out more'", required=False))]))], blank=True),
        ),
        migrations.AlterField(
            model_name='sectortag',
            name='body',
            field=wagtail.core.fields.StreamField([('rich_text', wagtail.core.blocks.RichTextBlock(features=['h2', 'h3', 'h4', 'h5', 'h6', 'bold', 'italic', 'small', 'ol', 'ul', 'link', 'document-link'])), ('embed', modules.content.blocks.stream.EmbedBlock()), ('table', wagtail.contrib.table_block.blocks.TableBlock()), ('pull_quote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.TextBlock(required=True))])), ('summary_box', wagtail.core.blocks.StructBlock([('text', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'small', 'ol', 'ul', 'link', 'document-link'], required=True))])), ('image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True))])), ('cta_block_form', wagtail.core.blocks.StructBlock([('link_type', wagtail.core.blocks.ChoiceBlock(choices=[('none', 'None'), ('page', 'Page'), ('document', 'Document'), ('url', 'URL')])), ('link_page', wagtail.core.blocks.PageChooserBlock(label='Linked Page', required=False)), ('link_document', wagtail.documents.blocks.DocumentChooserBlock(label='Linked Document', required=False)), ('link_url', wagtail.core.blocks.CharBlock(label='URL', required=False)), ('link_label', wagtail.core.blocks.CharBlock(help_text="If blank will display 'Find out more'", required=False))]))], blank=True),
        ),
    ]
