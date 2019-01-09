# filename: CSDNVisualize/CSDNCrawler/urls.py


from django.urls import path

from . import views


app_name = 'csdn_crawl'
urlpatterns = [
    #
    # Crawl
    #
    path('startcrawler/', views.startcrawler, name='startcrawler'),
    path('cleandata/', views.cleandata, name="cleandata"),

    path('loopArticles/', views.loopArticles, name="looparticles"),

    #
    # View data, or Visualize
    #
    path('', views.index, name='index'),
    # ex: domain:port/CSDNCrawler/5/
    path('<int:user_id_id>/', views.detail, name='detail'),


    #
    # DB API
    #
    path('userid/add/', views.userid_add, name='userid_add'),

    # follows
    path("userid/<int:pk>/follows/",
         views.follows_detail_of_userid, name="follows_detail_of_userid"),
    path("userid/<int:pk>/crawl/follows/",
         views.follows_crawl_of_userid, name="follows_crawl_of_userid"),
    path("userid/<int:pk>/get/follows/",
         views.follows_get_of_userid, name="follows_get_of_userid"),
]
