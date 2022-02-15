"""
    content.models.pages_types
    ~~~~~~~~~~~~~~~~~~~~~~~
    Core page types. Extend these to create the actual page models.

    ie: class ArticlePage(ContentPageType):
        [...]
"""

# 3rd party
from django.apps import apps
from django.db import models
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.utils.functional import cached_property
from django.utils.html import strip_tags

from wagtail.admin.edit_handlers import FieldPanel, ObjectList, TabbedInterface, StreamFieldPanel
from wagtail.core import fields
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.utils.decorators import cached_classmethod

from wagtailcache.cache import WagtailCacheMixin

# Project
from modules.core.models import UpdateBannerSettings
from modules.core.paginator import DiggPaginator
from modules.core.utils import get_site_context
from modules.content.blocks import (
    landing_page_blocks, article_page_body_blocks, contents_page_body_blocks,
)


####################################################################################################
# Core / general page types
####################################################################################################

class BasePage(WagtailCacheMixin, Page):

    class Meta:
        abstract = True

    thumbnail = models.ForeignKey(
        settings.IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    blurb = models.TextField(
        blank=True,
        null=True
    )

    display_date = models.DateField(
        blank=True,
        null=True,
        help_text="If blank, this will be set to the date the page was first published"
    )

    content_panels = Page.content_panels

    promote_panels = [
        ImageChooserPanel('thumbnail'),
        FieldPanel('blurb'),
    ] + Page.promote_panels

    settings_panels = [
        FieldPanel('display_date'),
    ] + Page.settings_panels

    search_fields = Page.search_fields + [
        index.SearchField('blurb'),
        index.SearchField('search_description'),
    ]

    @cached_property
    def breadcrumbs(self):
        ancestors = self.\
            get_ancestors()\
            .exclude(slug__in=['root', 'home'])\
            .values('title', 'url_path')
        breadcrumbs = []
        for page in ancestors:
            url = page.get('url_path', '').replace('/home', '', 1)
            breadcrumbs.append({'url': url, 'title': page.get('title')})
        return breadcrumbs

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        site = self.get_site()

        context.update(
            site_name=settings.SITE_NAME,
            **get_site_context(site),
            **UpdateBannerSettings.get_for_context(site, page=self),
            **self.get_metadata_settings(site)
        )

        return context

    @cached_classmethod
    def get_admin_tabs(cls):
        tabs = [
            (cls.content_panels, 'Content'),
            (cls.promote_panels, 'Promote'),
            (cls.settings_panels, 'Settings'),
        ]
        return tabs

    @cached_classmethod
    def get_edit_handler(cls):  # NOQA

        tabs = cls.get_admin_tabs()

        edit_handler = TabbedInterface([
            ObjectList(tab[0], heading=tab[1]) for tab in tabs
        ])

        return edit_handler.bind_to(model=cls)

    def get_meta_title(self):
        if self.seo_title:
            return self.seo_title
        else:
            return self.title

    def get_meta_description(self):
        if self.search_description:
            return self.search_description
        if getattr(self, 'blurb', False):
            return self.blurb
        try:
            for _ in self.body.stream_data:
                if _['type'] == 'rich_text':
                    return strip_tags(_['value'])
        except Exception:
            pass
        return None

    def get_metadata_settings(self, site):
        from modules.core.models import (
            MetaTagSettings
        )

        if not site:
            site = self.get_site()

        default_meta = MetaTagSettings.get_for_context(site)
        title = self.get_meta_title() or default_meta.get('meta_title')
        description = self.get_meta_description() or default_meta.get('meta_description')
        image = self.thumbnail or default_meta.get('meta_image')

        return {
            'meta_title': title,
            'meta_description': description,
            'meta_image': image
        }

    @cached_property
    def page_type(self):
        return str(self.__class__.__name__)


####################################################################################################
# Landing Page Type
####################################################################################################


class LandingPageType(BasePage):
    """
    A landing page is a curated content page meant as a jumping off point to lead users deeper
    into the content. It would typically be thematic.
    """

    class Meta:
        abstract = True

    body = fields.StreamField(landing_page_blocks, blank=True)

    model_content_panels = [
        StreamFieldPanel('body')
    ]

    content_panels = BasePage.content_panels + model_content_panels

    search_fields = BasePage.search_fields + [
        index.SearchField('body')
    ]

    def get_context(self, request, *args, **kwargs) -> dict:
        context = super().get_context(request, *args, **kwargs)
        context['body_classes'] = 'landing-page'
        return context


####################################################################################################
# Content Page Type
####################################################################################################

class ContentPageType(BasePage):
    """
    Typically used for articles, news posts, news etc.
    """

    class Meta:
        abstract = True

    template = 'content/article_page.jinja'

    body = fields.StreamField(article_page_body_blocks, blank=True)
    # additional_content = fields.StreamField(additional_content_blocks, blank=True)

    model_content_panels = [
        StreamFieldPanel('body'),
        # StreamFieldPanel('additional_content'),
    ]

    content_panels = BasePage.content_panels + model_content_panels

    search_fields = BasePage.search_fields + [
        index.SearchField('body'),
    ]

    @property
    def date(self):
        return self.display_date

    @cached_property
    def human_display_date(self):
        if self.display_date:
            return self.display_date.strftime('%d %B %Y')

    @property
    def display_title(self):
        "Allows us to override it for special cases"
        return self.title


# class ArticlePageWithContentsType(ContentPageType):
#     """
#     An article page which as a long body requiring a contents listing
#     """

#     class Meta:
#         abstract = True

#     template = 'content/article_page_with_contents.jinja'

#     body = fields.StreamField(contents_page_body_blocks, blank=True)

#     def build_contents_menu(self):
#         menu = []
#         for block in self.body:
#             if block.block_type == 'contents_menu_item':
#                 menu.append({
#                     'slug': block.value.slug,
#                     'title': block.value.get('title'),
#                     'children': []
#                 })
#             if block.block_type == 'contents_menu_sub_item':
#                 menu[-1]['children'].append({
#                     'slug': block.value.slug,
#                     'title': block.value.get('title')
#                 })
#         return menu

#     def get_context(self, request, *args, **kwargs):
#         context = super().get_context(request, *args, **kwargs)

#         context.update({
#             'contents_menu': self.build_contents_menu()
#         })

#         return context


####################################################################################################
# Index Page Type
####################################################################################################

class IndexPageType(BasePage):

    class Meta:
        abstract = True

    objects_model = None
    objects_per_page = 10

    paginator_class = DiggPaginator

    # See modules.core.paginator for what these mean:
    paginator_body = 5
    paginator_margin = 2
    paginator_padding = 2
    paginator_tail = 2

    intro = fields.RichTextField(
        blank=True, null=True, features=settings.RICHTEXT_INLINE_FEATURES,
    )

    # child_page_stream = fields.StreamField(
    #     additional_content_blocks,
    #     blank=True,
    #     help_text="The blocks you create here will be displayed below all child pages"
    # )

    content_panels = BasePage.content_panels + [
        FieldPanel('intro')
        # StreamFieldPanel('child_page_stream')
    ]

    def get_objects_model(self):
        if type(self.objects_model) is str:
            return apps.get_model(self.objects_model)

        return self.objects_model

    # def get_filter_options(self) -> dict:
    #     """
    #     This method should return a dict of valid filters for the child pages, in the format:

    #     {filterable_attribute: (value_field, label_field)}

    #     For example, given the objects_model model:

    #         NewsArticlePage(Page):
    #             ...
    #             categories = ParentalManyToManyField(
    #                 'taxonomy.NewsCategory',
    #                 related_name="news",
    #                 blank=True
    #             )

    #     returning {'categories': ('slug', 'name')}

    #     Means that you could create a series of checkboxes for each `NewsCategory`,
    #     where `slug` is the value, and `name` is label.
    #     """

    #     return {
    #         'categories': ('slug', 'name')
    #     }

    # def get_filter_label(self, model):
    #     """
    #     A simple method for getting the friendly name of a filter, in the case that you are
    #     setting up a loop in the template. Easily overridable with some "if field ==" logic,
    #     or just ignore it altogether and put a custom title on the template. You can do whatever
    #     you want. This is life.
    #     """

    #     return model._meta.verbose_name

    # def get_filter_data(self, request=None) -> dict:

    #     """
    #     Where to retrieve the filter data from. This is usually going to be from the query string
    #     but if you are passing via the url like /category/news/ then you could return view kwargs
    #     """
    #     return request.GET.copy()

    # def get_filters_for_template(self, request) -> dict:
    #     """
    #     This method return a list of dicts for constructing filter menus in the template.

    #     Each dict has a field_name, label and an is_active boolean to say whether this filter
    #     is currently being used on the queryset. Example:


    #     return [
    #         {
    #             'field_name': 'categories',
    #             'label': 'Category',
    #             'choices': <QuerySet [
    #                 {
    #                     'name': 'Blog',
    #                     'slug': 'blog',
    #                     'selected': True
    #                 },
    #                 {
    #                     'name': 'Press release',
    #                     'slug': 'press-release',
    #                     'selected': False
    #                 },

    #                 {
    #                     'name': 'Research Papers',
    #                     'slug': 'research',
    #                     'selected': False
    #                 },
    #             ]>
    #         }
    #     ]
    #     """

    #     filters = []
    #     query_string = request.GET.copy()
    #     objects_model = self.get_objects_model()

    #     for key, values in self.get_filter_options().items():
    #         filter_model = getattr(objects_model, key).field.related_model
    #         active_filters = query_string.getlist(key)

    #         value_key = values[0]

    #         choices = (
    #             filter_model
    #             .objects
    #             .values(*values)
    #             .annotate(
    #                 is_active=models.Case(
    #                     *[models.When(**{
    #                         value_key: active_filter,
    #                         'then': True
    #                     }) for active_filter in active_filters],
    #                     default=models.Value(False),
    #                     output_field=models.BooleanField()
    #                 )
    #             ).values(*values, 'is_active')
    #         )

    #         filters.append({
    #             'field_name': key,
    #             'label': self.get_filter_label(filter_model),
    #             'choices': choices
    #         })

    #     return filters

    def get_order_by(self):
        return ['-display_date', '-last_published_at']

    def base_queryset(self):
        return (
            self.get_objects_model()
            .objects
            .live()
            .select_related('thumbnail')
        )

    def get_queryset(self, request):

        """
        This returns the queryset needed to paginate the objects on the page. It pulls all the
        valid filters from get_filter_options and carries out the respective logic on the queryset.
        """

        query = self.base_queryset()
        # filter_options = self.get_filter_options()
        # filters = {}

        # for key, values in filter_options.items():
        #     query = query.prefetch_related(key)
        #     filter_value = request.GET.get(key, None)
        #     if filter_value:
        #         filters.update({
        #             f'{key}__{values[0]}': filter_value
        #         })

        # if filters:
        #     query = query.filter(**filters)

        return query.distinct().order_by(*self.get_order_by())

    def paginate_objects(self, request):
        queryset = self.get_queryset(request)
        paginator = self.paginator_class(
            queryset,
            self.objects_per_page,
            body=self.paginator_body,
            margin=self.paginator_margin,
            padding=self.paginator_padding,
            tail=self.paginator_tail,
        )
        current_page = request.GET.get('page', 1)
        try:
            return paginator.page(current_page)
        except PageNotAnInteger:
            return paginator.page(1)
        except EmptyPage:
            return paginator.page(paginator.num_pages)

    def get_context(self, request, *args, **kwargs) -> dict:
        context = super().get_context(request, *args, **kwargs)

        query_string = request.GET.copy()
        pagination_params = query_string.pop('page', None) and query_string.urlencode()

        context.update({
            # 'object_filters': self.get_filters_for_template(request),
            'page_obj': self.paginate_objects(request),
            'pagination_params': pagination_params
        })

        return context

    @classmethod
    def can_create_at(cls, parent) -> bool:
        return super().can_create_at(parent) and not cls.objects.exists()
