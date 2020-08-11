from django.urls import path
from modules.content import views

app_name = 'news'
urlpatterns = [
    path('', views.NewsIndexPageView.as_view(), name='index'),
    path('category/<slug:category_slug>/', views.NewsIndexPageView.as_view(), name='category'),
]
