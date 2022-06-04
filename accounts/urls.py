from django.urls import path
from . import views

#
# admin account : 
# #
# username: admin
# password: django1234
# 

app_name = "accounts"
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('request_login/', views.request_login, name='request_login'),
    path('register/', views.register, name='register'),
    path('request_register', views.request_register, name='request_register'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout, name='logout'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('save_profile_changes/', views.save_profile_changes, name='save_profile_changes'),
    path('change_password', views.change_password, name='change_password'),
    path('save_new_password', views.save_new_password, name='save_new_password'),


]
