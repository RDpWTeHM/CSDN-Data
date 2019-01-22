from django.urls import path, include

urlpatterns = [
    # "/api/v1/CSDNCrawler/"
    path('v1/CSDNCrawler/', include('CSDNCrawler.api.urls')),
]
