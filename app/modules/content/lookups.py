from ajax_select import LookupChannel
from django.core.exceptions import PermissionDenied


class BaseLookup(LookupChannel):

    def format_item_display(self, item):
        return u"<span class='tag'>%s</span>" % item.full_name

    def check_auth(self, request):
        roles = request.user.has_role(['Editor', 'Moderator'])
        staff = request.user.is_staff, request.user.is_superuser
        if not any([roles, staff]):
            raise PermissionDenied
