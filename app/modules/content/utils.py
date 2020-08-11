from django.conf import settings
from django.core.cache import cache
from django.db.models import F

from config.template import url_from_path


def cache_faqs():
    from modules.content.models import FAQItem

    cache.delete(settings.FAQS_CACHE_KEY)

    faqs = FAQItem.objects.annotate(
        page_url=F('faq_list__page_faq_list__page__url_path')
    ).values('pk', 'question', 'page_url')

    objs = {}

    for faq in faqs:
        pk, page_url = str(faq['pk']), faq['page_url']
        url = url_from_path(f'{page_url}#faq-{pk}')
        objs.update({pk: {'url': url, 'question': faq['question']}})
    cache.set(settings.FAQS_CACHE_KEY, objs)

    return objs


def get_faq(obj_pk):

    cached_faqs = cache.get(settings.FAQS_CACHE_KEY, {})
    obj = cached_faqs.get(obj_pk, None)

    if not obj:
        cached_faqs = cache_faqs()
        obj = cached_faqs.get(obj_pk, None)

    return obj


def get_faq_choices():
    from modules.content.models import FAQList
    faq_lists = FAQList.objects.prefetch_related('faqs').order_by('id')
    opts = []
    for faq_list in faq_lists:
        items = [(obj.pk, obj.question) for obj in faq_list.faqs.order_by('pk')]
        opts.append(
            (faq_list.name, items)
        )
    return opts
