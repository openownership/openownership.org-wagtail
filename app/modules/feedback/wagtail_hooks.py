from django.urls import path
from django.shortcuts import reverse

# from django.utils.translation import gettext_lazy as _
from wagtail.admin.menu import MenuItem, AdminOnlyMenuItem
from wagtail.core import hooks
# from wagtail.admin.menu import Menu, MenuItem, SubmenuMenuItem

# from .admin import urls as admin_urls
# from .admin.views import ExportFeedbackCSV

from .views.reports import FeedbackReportView


####################################################################################################
# Custom reports
####################################################################################################


@hooks.register('register_reports_menu_item')
def register_feedback_report_menu_item():
    return AdminOnlyMenuItem(
        FeedbackReportView.menu_title,
        reverse('feedback_report'),
        classnames='icon icon-' + FeedbackReportView.header_icon,
        order=700
    )

@hooks.register('register_admin_urls')
def register_feedback_report_url():
    return [
        path(
            'reports/feedback/',
            FeedbackReportView.as_view(),
            name='feedback_report'
        ),
    ]




# class FeedbackSubmenu(SubmenuMenuItem):
#     def is_shown(self, request):
#         user = request.user
#         if user.has_perm('feedback.view_feedback'):
#             return True

#         # Hardcoded groups access because groups admin fail
#         allowed_group_names = [
#             "Moderators",
#             "Editors",
#         ]
#         if user.groups.filter(name__in=allowed_group_names).count() > 0:
#             return True
#         else:
#             return False


# class FeedbackMenu(Menu):
#     def __init__(self):
#         self._registered_menu_items = [
#             MenuItem(
#                 _('Ratings'),
#                 reverse('feedback_admin:ratings'),
#                 classnames='icon icon-fa-star-half-o',
#                 order=10
#             ),
#             MenuItem(
#                 _('Comments'),
#                 reverse('feedback_admin:comments'),
#                 classnames='icon icon-fa-comments',
#                 order=20
#             ),
#         ]

#         self.construct_hook_name = None


# @hooks.register('register_admin_urls')
# def register_admin_urls():
#     return [
#         url(r'^feedback/', include((admin_urls, 'feedback'), namespace='feedback_admin')),
#         path('feedback/export/', ExportFeedbackCSV.as_view(), name="feedback_export"),
#     ]


# @hooks.register('register_admin_menu_item')
# def register_feedback_menu_item():
#     clubs_menu = FeedbackMenu()
#     return FeedbackSubmenu(
#         _('Feedback'),
#         clubs_menu,
#         classnames='icon icon-fa-star-half-o',
#         order=800
#     )
