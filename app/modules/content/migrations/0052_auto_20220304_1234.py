# Generated by Django 3.2.12 on 2022-03-04 12:34

from django.db import migrations
import modules.content.blocks.stream
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.snippets.blocks
import wagtailmodelchooser.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0051_merge_0046_mappage_0050_presslinkspage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homepage',
            name='body',
            field=wagtail.core.fields.StreamField([('highlight_pages', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='e.g. “Examples of our work”, or leave empty', required=False)), ('pages', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('page', wagtail.core.blocks.PageChooserBlock(required=True)), ('card_format', wagtail.core.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')]))]), min_num=1))])), ('latest_section_content', wagtail.core.blocks.StructBlock([('section_page', wagtail.core.blocks.PageChooserBlock(label='Front page of section', page_type=['content.SectionPage'], required=True))])), ('latest_by_focus_area', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='If blank, will use "Latest"', required=False)), ('focus_area', wagtailmodelchooser.blocks.ModelChooserBlock(required=True, target_model='taxonomy.focusareatag'))])), ('latest_by_publication_type', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='If blank, will use "Latest"', required=False)), ('publication_type', wagtailmodelchooser.blocks.ModelChooserBlock(required=True, target_model='taxonomy.publicationtype'))])), ('latest_by_sector', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='If blank, will use "Latest"', required=False)), ('sector', wagtailmodelchooser.blocks.ModelChooserBlock(required=True, target_model='taxonomy.sectortag'))]))], blank=True),
        ),
        migrations.AlterField(
            model_name='sectionpage',
            name='body',
            field=wagtail.core.fields.StreamField([('highlight_pages', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='e.g. “Examples of our work”, or leave empty', required=False)), ('pages', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('page', wagtail.core.blocks.PageChooserBlock(required=True)), ('card_format', wagtail.core.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')]))]), min_num=1))])), ('areas_of_focus_block', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='Leave empty to use default: "Areas of Focus"', required=False)), ('card_format', wagtail.core.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')])), ('tags', wagtail.core.blocks.ListBlock(wagtail.snippets.blocks.SnippetChooserBlock('taxonomy.FocusAreaTag', required=True), label='Areas of Focus', max_num=3, min_num=1))])), ('sectors_block', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='Leave empty to use default: "Sectors"', required=False)), ('card_format', wagtail.core.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')])), ('tags', wagtail.core.blocks.ListBlock(wagtail.snippets.blocks.SnippetChooserBlock('taxonomy.SectorTag', required=True), label='Sectors', max_num=3, min_num=1))])), ('latest_section_content', wagtail.core.blocks.StructBlock([('section_page', wagtail.core.blocks.PageChooserBlock(label='Front page of section', page_type=['content.SectionPage'], required=True))])), ('publication_types', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='Leave empty to use default: "View by publication type"', required=False)), ('card_format', wagtail.core.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')])), ('types', wagtail.core.blocks.MultipleChoiceBlock(choices=modules.content.blocks.stream.get_publication_type_choices))])), ('press_links', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='Leave empty to use default: "Press links"', required=False)), ('card_format', wagtail.core.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')])), ('limit_number', wagtail.core.blocks.IntegerBlock(default=3, required=True))]))], blank=True),
        ),
    ]
