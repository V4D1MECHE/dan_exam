from django.urls import path
from . import views

urlpatterns = [
    path('', views.resume_list, name='resume_list'),
    path('resume/<int:pk>/', views.resume_detail, name='resume_detail'),
    path('my-resumes/', views.my_resumes, name='my_resumes'),
    path('templates/', views.template_list, name='template_list'),
]