from django.urls import path
from . import views

#
# admin account : 
# #
# username: admin
# password: django1234
# 

app_name = 'file_manager'
urlpatterns = [
    path('', views.index, name='index'),
    path('upload_file/', views.upload_file, name='upload_file'),
    path('admin_categories/', views.admin_categories, name='admin_categories'),
    path('save_category_changes/', views.save_category_changes, name='save_category_changes'),
    path('delete_selected_categories/', views.delete_selected_categories, name='delete_selected_categories'),
    path('admin_save_new_category/', views.admin_save_new_category, name='admin_save_new_category'),
    path('admin_get_category_details/', views.admin_get_category_details, name='admin_get_category_details'),
    path('admin_users/', views.admin_users, name='admin_users'),
    path('admin_save_profile_changes/', views.admin_save_profile_changes, name='admin_save_profile_changes'),
    path('admin_add_user/', views.admin_add_user, name='admin_add_user'),
    path('admin_delete_selected_users/', views.admin_delete_selected_users, name='admin_delete_selected_users'),
    path('admin_get_user_details/', views.admin_get_user_details, name='admin_get_user_details'),
    path('delete_selected_files/', views.delete_selected_files, name='delete_selected_files'),
    path('get_file_details/', views.get_file_details, name='get_file_details'),
    path('save_file_changes', views.save_file_changes, name='save_file_changes'),
    path('file_view/<int:file_id>', views.file_view, name='file_view'),
    path('archives/', views.archives, name='archives'),
    path('restore_selected_files/', views.restore_selected_files, name='restore_selected_files'),
    path('restore_selected_users/', views.restore_selected_users, name='restore_selected_users'),
    path('restore_selected_categories/', views.restore_selected_categories, name='restore_selected_categories'),
    





]
