from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('veexam/', views.veexam_list, name='veexam_list'),
]