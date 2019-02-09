from django.urls import path, re_path, include

urlpatterns = [
    # "/api/v1/CSDNCrawler/"
    path('v1/CSDNCrawler/', include('CSDNCrawler.api.urls')),
    re_path(r'^rest_auth/', include('rest_auth.urls')),
]
