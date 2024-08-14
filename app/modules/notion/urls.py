from django.urls import path

from .views import serve_csv_file

urlpatterns = [
    path("metadata.csv", serve_csv_file, name="serve_csv_file"),
]
