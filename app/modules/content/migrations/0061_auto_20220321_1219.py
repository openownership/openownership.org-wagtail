# Generated by Django 3.2.12 on 2022-03-21 12:19

from django.db import migrations
import modules.content.blocks.stream
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.snippets.blocks
import wagtailmodelchooser.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0060_publicationfrontpage_show_display_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articlepage',
            name='additional_content',
            field=wagtail.core.fields.StreamField([('similar_content', wagtail.core.blocks.StructBlock([('suggest_by', wagtail.core.blocks.ChoiceBlock(choices=[('sector', 'Topic'), ('publication_type', 'Content Type'), ('author', 'Author'), ('country', 'Country'), ('section', 'Section'), ('principles', 'Open Ownership Principles')]))])), ('highlight_pages', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='e.g. “Examples of our work”, or leave empty', required=False)), ('pages', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('page', wagtail.core.blocks.PageChooserBlock(required=True)), ('card_format', wagtail.core.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')]))]), min_num=1))]))], blank=True),
        ),
        migrations.AlterField(
            model_name='blogarticlepage',
            name='additional_content',
            field=wagtail.core.fields.StreamField([('similar_content', wagtail.core.blocks.StructBlock([('suggest_by', wagtail.core.blocks.ChoiceBlock(choices=[('sector', 'Topic'), ('publication_type', 'Content Type'), ('author', 'Author'), ('country', 'Country'), ('section', 'Section'), ('principles', 'Open Ownership Principles')]))])), ('highlight_pages', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='e.g. “Examples of our work”, or leave empty', required=False)), ('pages', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('page', wagtail.core.blocks.PageChooserBlock(required=True)), ('card_format', wagtail.core.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')]))]), min_num=1))]))], blank=True),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='body',
            field=wagtail.core.fields.StreamField([('highlight_pages', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='e.g. “Examples of our work”, or leave empty', required=False)), ('pages', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('page', wagtail.core.blocks.PageChooserBlock(required=True)), ('card_format', wagtail.core.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')]))]), min_num=1))])), ('publication_types', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='Leave empty to use default: "View by publication type"', required=False)), ('card_format', wagtail.core.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')])), ('types', wagtail.core.blocks.MultipleChoiceBlock(choices=modules.content.blocks.stream.get_publication_type_choices))], label='Content types')), ('latest_section_content', wagtail.core.blocks.StructBlock([('section_page', wagtail.core.blocks.PageChooserBlock(label='Front page of section', page_type=['content.SectionPage'], required=True))])), ('latest_by_publication_type', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='If blank, will use "Latest"', required=False)), ('publication_type', wagtailmodelchooser.blocks.ModelChooserBlock(required=True, target_model='taxonomy.publicationtype'))], label='Latest by content type')), ('latest_by_topic', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='If blank, will use "Latest"', required=False)), ('sector', wagtailmodelchooser.blocks.ModelChooserBlock(required=True, target_model='taxonomy.sectortag'))])), ('latest_by_section_tag', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='If blank, will use "Latest"', required=False)), ('section', wagtailmodelchooser.blocks.ModelChooserBlock(required=True, target_model='taxonomy.sectiontag'))])), ('latest_by_open_ownership_principle', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='If blank, will use "Latest"', required=False)), ('principle', wagtailmodelchooser.blocks.ModelChooserBlock(required=True, target_model='taxonomy.principletag'))])), ('latest_from_the_blog', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(default='Latest blog posts', required=True)), ('section', wagtailmodelchooser.blocks.ModelChooserBlock(help_text='', required=False, target_model='taxonomy.sectiontag'))])), ('latest_news', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(default='Latest news', required=True)), ('section', wagtailmodelchooser.blocks.ModelChooserBlock(help_text='', required=False, target_model='taxonomy.sectiontag'))])), ('latest_publications', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(default='Latest publications', required=True)), ('section', wagtailmodelchooser.blocks.ModelChooserBlock(help_text='', required=False, target_model='taxonomy.sectiontag'))])), ('latest_content', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(default='Latest', required=True)), ('section', wagtailmodelchooser.blocks.ModelChooserBlock(help_text='', required=False, target_model='taxonomy.sectiontag'))]))], blank=True),
        ),
        migrations.AlterField(
            model_name='jobpage',
            name='additional_content',
            field=wagtail.core.fields.StreamField([('similar_content', wagtail.core.blocks.StructBlock([('suggest_by', wagtail.core.blocks.ChoiceBlock(choices=[('sector', 'Topic'), ('publication_type', 'Content Type'), ('author', 'Author'), ('country', 'Country'), ('section', 'Section'), ('principles', 'Open Ownership Principles')]))])), ('highlight_pages', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='e.g. “Examples of our work”, or leave empty', required=False)), ('pages', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('page', wagtail.core.blocks.PageChooserBlock(required=True)), ('card_format', wagtail.core.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')]))]), min_num=1))]))], blank=True),
        ),
        migrations.AlterField(
            model_name='newsarticlepage',
            name='additional_content',
            field=wagtail.core.fields.StreamField([('similar_content', wagtail.core.blocks.StructBlock([('suggest_by', wagtail.core.blocks.ChoiceBlock(choices=[('sector', 'Topic'), ('publication_type', 'Content Type'), ('author', 'Author'), ('country', 'Country'), ('section', 'Section'), ('principles', 'Open Ownership Principles')]))])), ('highlight_pages', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='e.g. “Examples of our work”, or leave empty', required=False)), ('pages', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('page', wagtail.core.blocks.PageChooserBlock(required=True)), ('card_format', wagtail.core.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')]))]), min_num=1))]))], blank=True),
        ),
        migrations.AlterField(
            model_name='publicationfrontpage',
            name='additional_content',
            field=wagtail.core.fields.StreamField([('similar_content', wagtail.core.blocks.StructBlock([('suggest_by', wagtail.core.blocks.ChoiceBlock(choices=[('sector', 'Topic'), ('publication_type', 'Content Type'), ('author', 'Author'), ('country', 'Country'), ('section', 'Section'), ('principles', 'Open Ownership Principles')]))])), ('highlight_pages', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='e.g. “Examples of our work”, or leave empty', required=False)), ('pages', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('page', wagtail.core.blocks.PageChooserBlock(required=True)), ('card_format', wagtail.core.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')]))]), min_num=1))]))], blank=True),
        ),
        migrations.AlterField(
            model_name='publicationinnerpage',
            name='additional_content',
            field=wagtail.core.fields.StreamField([('similar_content', wagtail.core.blocks.StructBlock([('suggest_by', wagtail.core.blocks.ChoiceBlock(choices=[('sector', 'Topic'), ('publication_type', 'Content Type'), ('author', 'Author'), ('country', 'Country'), ('section', 'Section'), ('principles', 'Open Ownership Principles')]))])), ('highlight_pages', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='e.g. “Examples of our work”, or leave empty', required=False)), ('pages', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('page', wagtail.core.blocks.PageChooserBlock(required=True)), ('card_format', wagtail.core.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')]))]), min_num=1))]))], blank=True),
        ),
        migrations.AlterField(
            model_name='sectionpage',
            name='body',
            field=wagtail.core.fields.StreamField([('highlight_pages', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='e.g. “Examples of our work”, or leave empty', required=False)), ('pages', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('page', wagtail.core.blocks.PageChooserBlock(required=True)), ('card_format', wagtail.core.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')]))]), min_num=1))])), ('topics_block', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='Leave empty to use default: "Topics"', required=False)), ('card_format', wagtail.core.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')])), ('tags', wagtail.core.blocks.ListBlock(wagtail.snippets.blocks.SnippetChooserBlock('taxonomy.SectorTag', required=True), label='Topics', max_num=3, min_num=1))], label='Topics')), ('latest_section_content', wagtail.core.blocks.StructBlock([('section_page', wagtail.core.blocks.PageChooserBlock(label='Front page of section', page_type=['content.SectionPage'], required=True))])), ('publication_types', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='Leave empty to use default: "View by publication type"', required=False)), ('card_format', wagtail.core.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')])), ('types', wagtail.core.blocks.MultipleChoiceBlock(choices=modules.content.blocks.stream.get_publication_type_choices))], label='Content types')), ('press_links', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='Leave empty to use default: "Press links"', required=False)), ('card_format', wagtail.core.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')])), ('limit_number', wagtail.core.blocks.IntegerBlock(default=3, required=True))])), ('latest_from_the_blog', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(default='Latest blog posts', required=True)), ('section', wagtailmodelchooser.blocks.ModelChooserBlock(help_text='', required=False, target_model='taxonomy.sectiontag'))])), ('latest_news', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(default='Latest news', required=True)), ('section', wagtailmodelchooser.blocks.ModelChooserBlock(help_text='', required=False, target_model='taxonomy.sectiontag'))])), ('latest_publications', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(default='Latest publications', required=True)), ('section', wagtailmodelchooser.blocks.ModelChooserBlock(help_text='', required=False, target_model='taxonomy.sectiontag'))]))], blank=True),
        ),
        migrations.AlterField(
            model_name='utilitypage',
            name='additional_content',
            field=wagtail.core.fields.StreamField([('similar_content', wagtail.core.blocks.StructBlock([('suggest_by', wagtail.core.blocks.ChoiceBlock(choices=[('sector', 'Topic'), ('publication_type', 'Content Type'), ('author', 'Author'), ('country', 'Country'), ('section', 'Section'), ('principles', 'Open Ownership Principles')]))])), ('highlight_pages', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='e.g. “Examples of our work”, or leave empty', required=False)), ('pages', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('page', wagtail.core.blocks.PageChooserBlock(required=True)), ('card_format', wagtail.core.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')]))]), min_num=1))]))], blank=True),
        ),
    ]
