from django.urls import path
from . import views

app_name = 'reports'
urlpatterns = [
    path('', views.reports, name='index'),
    path('get_users', views.get_users, name='get_users'),
    path('get_files', views.get_files, name='get_files'),
    path('get_logs', views.get_logs, name='get_logs'),

]