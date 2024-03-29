# Generated by Django 3.2.12 on 2022-03-24 15:57

from django.db import migrations
import modules.content.blocks.stream
import wagtail.blocks
import wagtail.fields
import wagtail.snippets.blocks
import wagtailmodelchooser.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0062_auto_20220324_1227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sectionpage',
            name='body',
            field=wagtail.fields.StreamField([('highlight_pages', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(help_text='e.g. “Examples of our work”, or leave empty', required=False)), ('pages', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(required=True)), ('card_format', wagtail.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')]))]), min_num=1))])), ('topics_block', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(help_text='Leave empty to use default: "Topics"', required=False)), ('card_format', wagtail.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')])), ('tags', wagtail.blocks.ListBlock(wagtail.snippets.blocks.SnippetChooserBlock('taxonomy.SectorTag', required=True), label='Topics', max_num=3, min_num=1))], label='Topics')), ('latest_section_content', wagtail.blocks.StructBlock([('section_page', wagtail.blocks.PageChooserBlock(label='Front page of section', page_type=['content.SectionPage'], required=True))])), ('publication_types', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(help_text='Leave empty to use default: "View by publication type"', required=False)), ('card_format', wagtail.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')])), ('types', wagtail.blocks.MultipleChoiceBlock(choices=modules.content.blocks.stream.get_publication_type_choices))], label='Content types')), ('press_links', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(help_text='Leave empty to use default: "Press links"', required=False)), ('section', wagtailmodelchooser.blocks.ModelChooserBlock(help_text='Optional, restrict to press links tagged by section', required=False, target_model='taxonomy.sectiontag')), ('limit_number', wagtail.blocks.IntegerBlock(default=3, required=True))])), ('latest_from_the_blog', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(default='Latest blog posts', required=True)), ('section', wagtailmodelchooser.blocks.ModelChooserBlock(help_text='', required=False, target_model='taxonomy.sectiontag'))])), ('latest_news', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(default='Latest news', required=True)), ('section', wagtailmodelchooser.blocks.ModelChooserBlock(help_text='', required=False, target_model='taxonomy.sectiontag'))])), ('latest_publications', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(default='Latest publications', required=True)), ('section', wagtailmodelchooser.blocks.ModelChooserBlock(help_text='', required=False, target_model='taxonomy.sectiontag'))]))], blank=True),
        ),
    ]
