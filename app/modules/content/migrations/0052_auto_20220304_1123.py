# Generated by Django 3.2.12 on 2022-03-04 11:23

from django.db import migrations
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0051_merge_0046_mappage_0050_presslinkspage'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlepage',
            name='additional_content',
            field=wagtail.fields.StreamField([('similar_content', wagtail.blocks.StructBlock([('suggest_by', wagtail.blocks.ChoiceBlock(choices=[('focus_area', 'Area of Focus'), ('sector', 'Sector'), ('publication_type', 'Publication Type'), ('author', 'Author')]))])), ('highlight_pages', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(help_text='e.g. “Examples of our work”, or leave empty', required=False)), ('pages', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(required=True)), ('card_format', wagtail.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')]))]), min_num=1))]))], blank=True),
        ),
        migrations.AddField(
            model_name='blogarticlepage',
            name='additional_content',
            field=wagtail.fields.StreamField([('similar_content', wagtail.blocks.StructBlock([('suggest_by', wagtail.blocks.ChoiceBlock(choices=[('focus_area', 'Area of Focus'), ('sector', 'Sector'), ('publication_type', 'Publication Type'), ('author', 'Author')]))])), ('highlight_pages', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(help_text='e.g. “Examples of our work”, or leave empty', required=False)), ('pages', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(required=True)), ('card_format', wagtail.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')]))]), min_num=1))]))], blank=True),
        ),
        migrations.AddField(
            model_name='jobpage',
            name='additional_content',
            field=wagtail.fields.StreamField([('similar_content', wagtail.blocks.StructBlock([('suggest_by', wagtail.blocks.ChoiceBlock(choices=[('focus_area', 'Area of Focus'), ('sector', 'Sector'), ('publication_type', 'Publication Type'), ('author', 'Author')]))])), ('highlight_pages', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(help_text='e.g. “Examples of our work”, or leave empty', required=False)), ('pages', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(required=True)), ('card_format', wagtail.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')]))]), min_num=1))]))], blank=True),
        ),
        migrations.AddField(
            model_name='newsarticlepage',
            name='additional_content',
            field=wagtail.fields.StreamField([('similar_content', wagtail.blocks.StructBlock([('suggest_by', wagtail.blocks.ChoiceBlock(choices=[('focus_area', 'Area of Focus'), ('sector', 'Sector'), ('publication_type', 'Publication Type'), ('author', 'Author')]))])), ('highlight_pages', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(help_text='e.g. “Examples of our work”, or leave empty', required=False)), ('pages', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(required=True)), ('card_format', wagtail.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')]))]), min_num=1))]))], blank=True),
        ),
        migrations.AddField(
            model_name='publicationfrontpage',
            name='additional_content',
            field=wagtail.fields.StreamField([('similar_content', wagtail.blocks.StructBlock([('suggest_by', wagtail.blocks.ChoiceBlock(choices=[('focus_area', 'Area of Focus'), ('sector', 'Sector'), ('publication_type', 'Publication Type'), ('author', 'Author')]))])), ('highlight_pages', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(help_text='e.g. “Examples of our work”, or leave empty', required=False)), ('pages', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(required=True)), ('card_format', wagtail.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')]))]), min_num=1))]))], blank=True),
        ),
        migrations.AddField(
            model_name='publicationinnerpage',
            name='additional_content',
            field=wagtail.fields.StreamField([('similar_content', wagtail.blocks.StructBlock([('suggest_by', wagtail.blocks.ChoiceBlock(choices=[('focus_area', 'Area of Focus'), ('sector', 'Sector'), ('publication_type', 'Publication Type'), ('author', 'Author')]))])), ('highlight_pages', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(help_text='e.g. “Examples of our work”, or leave empty', required=False)), ('pages', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(required=True)), ('card_format', wagtail.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')]))]), min_num=1))]))], blank=True),
        ),
        migrations.AddField(
            model_name='utilitypage',
            name='additional_content',
            field=wagtail.fields.StreamField([('similar_content', wagtail.blocks.StructBlock([('suggest_by', wagtail.blocks.ChoiceBlock(choices=[('focus_area', 'Area of Focus'), ('sector', 'Sector'), ('publication_type', 'Publication Type'), ('author', 'Author')]))])), ('highlight_pages', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(help_text='e.g. “Examples of our work”, or leave empty', required=False)), ('pages', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(required=True)), ('card_format', wagtail.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('portrait', 'Portrait')]))]), min_num=1))]))], blank=True),
        ),
    ]
