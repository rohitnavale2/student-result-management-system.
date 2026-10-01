"""
URL configuration for project_2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app1 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='Home'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('create-Class/', views.create_class, name='create_class'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('manage-classes/', views.manage_classes, name='manage_classes'),
    path('edit-class/<int:class_id>/', views.edit_class, name='edit_class'),
    path('delete-class/<int:class_id>/', views.delete_class, name='delete_class'),
    path("create-subject/", views.create_subject, name="create_subject"),
    path("create-subject-combination/", views.create_subject_combination, name="create_subject_combination"),
    path("manage-subjects/", views.manage_subjects, name="manage_subjects"),
    path("edit-subject/<int:subject_id>/", views.edit_subject, name="edit_subject"),
    path("delete-subject/<int:subject_id>/", views.delete_subject, name="delete_subject"),
    path("manage-subject-combinations/", views.manage_subject_combinations, name="manage_subject_combinations"),
    path("edit-subject-combination/<int:combination_id>/", views.edit_subject_combination, name="edit_subject_combination"),
    path("delete-subject-combination/<int:combination_id>/", views.delete_subject_combination, name="delete_subject_combination"),
    path("add-student/", views.add_student, name="add_student"),
    path("manage-students/", views.manage_students, name="manage_students"),
    path("edit-student/<int:student_id>/", views.edit_student, name="edit_student"),
    path("delete-student/<int:student_id>/", views.delete_student, name="delete_student"),
    path("add-notice/", views.add_notice, name="add_notice"),
    path("manage-notices/", views.manage_notices, name="manage_notices"),
    path("edit-notice/<int:notice_id>/", views.edit_notice, name="edit_notice"),path("add-result/", views.add_result, name="add_result"),
    path("manage-results/", views.manage_results, name="manage_results"),
    path("edit-result/<int:result_id>/", views.edit_result, name="edit_result"),
    path("delete-result/<int:result_id>/", views.delete_result, name="delete_result"),
    path("delete-notice/<int:notice_id>/", views.delete_notice, name="delete_notice"),
    path("change-password/", views.change_password, name="change_password"),
    path("download-result/<int:student_id>/", views.download_result, name="download_result"),
    


    
]