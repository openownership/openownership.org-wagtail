# Generated by Django 3.1.14 on 2022-02-09 14:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0017_blogarticlepage_blogindexpage_newsarticlepage_newsindexpage_themepage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='faqitem',
            name='faq_list',
        ),
        migrations.DeleteModel(
            name='NewsCategory',
        ),
        migrations.RemoveField(
            model_name='pagefaqlist',
            name='faq_list',
        ),
        migrations.RemoveField(
            model_name='pagefaqlist',
            name='page',
        ),
        migrations.DeleteModel(
            name='FAQItem',
        ),
        migrations.DeleteModel(
            name='FAQList',
        ),
        migrations.DeleteModel(
            name='PageFAQList',
        ),
    ]
