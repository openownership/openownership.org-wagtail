from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.RatingsView.as_view(), name='ratings'),
    url(r'^comments/$', views.CommentsView.as_view(), name='comments')

]
