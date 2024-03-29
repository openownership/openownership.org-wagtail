# Generated by Django 3.1.14 on 2022-02-23 15:39

from django.db import migrations
import wagtail.blocks
import wagtail.fields
import wagtail.snippets.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0031_add_area_of_focus_and_sector_blocks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homepage',
            name='body',
            field=wagtail.fields.StreamField([('latest_section_content', wagtail.blocks.StructBlock([('section_page', wagtail.blocks.PageChooserBlock(label='Front page of section', page_type=['content.SectionPage'], required=True))]))], blank=True),
        ),
        migrations.AlterField(
            model_name='sectionpage',
            name='body',
            field=wagtail.fields.StreamField([('areas_of_focus_block', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(help_text='Leave empty to use default: "Areas of Focus"', required=False)), ('tags', wagtail.blocks.ListBlock(wagtail.snippets.blocks.SnippetChooserBlock('taxonomy.FocusAreaTag', required=True), label='Areas of Focus', max_num=3, min_num=1))])), ('sectors_block', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(help_text='Leave empty to use default: "Sectors"', required=False)), ('tags', wagtail.blocks.ListBlock(wagtail.snippets.blocks.SnippetChooserBlock('taxonomy.SectorTag', required=True), label='Sectors', max_num=3, min_num=1))])), ('latest_section_content', wagtail.blocks.StructBlock([('section_page', wagtail.blocks.PageChooserBlock(label='Front page of section', page_type=['content.SectionPage'], required=True))]))], blank=True),
        ),
    ]
