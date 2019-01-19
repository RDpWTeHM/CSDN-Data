from django.urls import path, re_path
from django.http import HttpResponse


urlpatterns = [
    # handler "/api/v1/CSDNCrawler/[.../]"
    path("", lambda request: HttpResponse("<h1>DRF => CSDNVisualize > CSDNCrawler</h1>")),

]
