from django.urls import path, re_path
from django.http import HttpResponse

from .views import UserIDList
from .views import UserIDDetail

from .views import VisualDataList
from .views import VisualDataDetail

from .views import FansList
from .views import FansDetail
from .views import FollowList, FollowDetail


urlpatterns = [
    # handler "/api/v1/CSDNCrawler/[.../]"
    path("", lambda request: HttpResponse("<h1>DRF => CSDNVisualize > CSDNCrawler</h1>")),

    #
    # /userids/[.../]
    #
    # [{}/] ###################
    path("userids/",                UserIDList.as_view(), name="userids_list"),
    path("userids/<str:user_id>/", UserIDDetail.as_view(), name="userids_detail"),

    # visualdatas/[{}/]
    path("userids/<str:user_id>/visualdatas/",            VisualDataList.as_view(), name="visualdatas_list"),
    path("userids/<str:user_id>/visualdatas/<str:date>/", VisualDataDetail.as_view(), name="visualdatas_detail"),

    # fanses/[{}/] #########################
    path("userids/<str:user_id>/fanses/",                FansList.as_view(), name="fanses_list"),
    path("userids/<str:user_id>/fanses/<int:fans_idx>/", FansDetail.as_view(), name="fanses_detail"),

    # follows/[{}/] ########################
    path("userids/<str:user_id>/follows/",                  FollowList.as_view(), name="follow_list"),
    path("userids/<str:user_id>/follows/<int:follow_idx>/", FollowDetail.as_view(), name="follow_detail"),
]
