from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [ 

    path('', views.home, name='home'),
    path('add-file/', views.addFile, name='add-file'),
    path('add-group/', views.addGroup, name='add-group'),
    path('all-groups/', views.allGroups, name='all-groups'),
    path('checkin/<str:id>',views.checkin, name='checkin'),
    path('check-file-status/<str:id>',views.check_file_status, name='check-file-status'),
    path('group-checkin/<str:id>',views.groupCheckin, name='group-checkin'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('download-file/<str:id>', views.downloadFile, name='download-file'),
    path('generate-report/<str:id>', views.generateReport, name='generate-report'),
    path('delete-file/<str:id>', views.deleteFile, name='delete-file'),
    path('delete-group/<str:id>', views.deleteGroup, name='delete-group'),
    path('search/', views.search, name='search'),
    path('favicon.ico', views.favicon_view),

    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)