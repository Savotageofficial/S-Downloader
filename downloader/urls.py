from django.urls import path

from downloader import views

urlpatterns = [
    path('download-android/' , views.download_android),
    path('download-app/', views.download_app, name='download_app'),
    path("" , views.home , name="downloader"),
    path("download_options/" , views.show_download_options , name="show_download_options"),
    path("download/" , views.download , name="download"),
    path("robots.txt", views.robots_txt),

]
