from django.urls import path, re_path
from django.http import HttpResponse

from .views import FansList
from .views import FansDetail


urlpatterns = [
    # handler "/api/v1/CSDNCrawler/[.../]"
    path("", lambda request: HttpResponse("<h1>DRF => CSDNVisualize > CSDNCrawler</h1>")),

    #
    # /userids/[.../]
    #
    # n/a... ###################
    # path("userids/<str:user_ids>/"),

    # fanses/[{}/] #########################
    path("userids/<str:user_id>/fanses/",                FansList.as_view(), name="fans_list"),
    path("userids/<str:user_id>/fanses/<int:fans_idx>/", FansDetail.as_view(), name="fans_detail"),

    # follows/[{}/] ########################
]
