# Generated by Django 3.2.12 on 2022-02-24 18:56

from django.db import migrations
import modules.content.blocks.stream
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.snippets.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0032_auto_20220223_1539'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sectionpage',
            name='body',
            field=wagtail.core.fields.StreamField([('areas_of_focus_block', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='Leave empty to use default: "Areas of Focus"', required=False)), ('tags', wagtail.core.blocks.ListBlock(wagtail.snippets.blocks.SnippetChooserBlock('taxonomy.FocusAreaTag', required=True), label='Areas of Focus', max_num=3, min_num=1))])), ('sectors_block', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='Leave empty to use default: "Sectors"', required=False)), ('tags', wagtail.core.blocks.ListBlock(wagtail.snippets.blocks.SnippetChooserBlock('taxonomy.SectorTag', required=True), label='Sectors', max_num=3, min_num=1))])), ('latest_section_content', wagtail.core.blocks.StructBlock([('section_page', wagtail.core.blocks.PageChooserBlock(label='Front page of section', page_type=['content.SectionPage'], required=True))])), ('publication_types', wagtail.core.blocks.StructBlock([('section_page', wagtail.core.blocks.PageChooserBlock(help_text='Link to Publication Types within this section', label='Front page of section', page_type=['content.SectionPage'], required=True)), ('title', wagtail.core.blocks.CharBlock(help_text='Leave empty to use default: "View by publication type"', required=False)), ('types', wagtail.core.blocks.MultipleChoiceBlock(choices=modules.content.blocks.stream.get_publication_type_choices))]))], blank=True),
        ),
    ]
