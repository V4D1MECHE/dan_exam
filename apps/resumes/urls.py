from django.urls import path
from . import views

urlpatterns = [
    path('', views.resume_list, name='resume_list'),
    path('resume/<int:pk>/', views.resume_detail, name='resume_detail'),
    path('my-resumes/', views.my_resumes, name='my_resumes'),
    path('templates/', views.template_list, name='template_list'),
    
    # CRUD для резюме
    path('resume/create/', views.ResumeCreateView.as_view(), name='resume_create'),
    path('resume/<int:pk>/update/', views.ResumeUpdateView.as_view(), name='resume_update'),
    path('resume/<int:pk>/delete/', views.ResumeDeleteView.as_view(), name='resume_delete'),
    
    # CRUD для навыков
    path('resume/<int:resume_pk>/skill/create/', views.skill_create, name='skill_create'),
    path('skill/<int:pk>/update/', views.skill_update, name='skill_update'),
    path('skill/<int:pk>/delete/', views.skill_delete, name='skill_delete'),
    path('resume/<int:resume_pk>/manage-skills/', views.manage_resume_skills, name='manage_resume_skills'),
    
    # CRUD для опыта работы
    path('resume/<int:resume_pk>/work-experience/create/', views.WorkExperienceCreateView.as_view(), name='work_experience_create'),
    
    # CRUD для образования
    path('resume/<int:resume_pk>/education/create/', views.EducationCreateView.as_view(), name='education_create'),
    
    # CRUD для контактов
    path('resume/<int:resume_pk>/contact/create/', views.contact_create, name='contact_create'),
    path('contact/<int:pk>/update/', views.contact_update, name='contact_update'),
    path('contact/<int:pk>/delete/', views.contact_delete, name='contact_delete'),
    
    # CRUD для языков
    path('resume/<int:resume_pk>/language/create/', views.language_create, name='language_create'),
    path('language/<int:pk>/update/', views.language_update, name='language_update'),
    path('language/<int:pk>/delete/', views.language_delete, name='language_delete'),
    
    # Управление тегами навыков - COMMENTED OUT: SkillTag models no longer exist
    # path('skill-tags/', views.SkillTagListView.as_view(), name='skilltag_list'),
    # path('skill-tags/create/', views.SkillTagCreateView.as_view(), name='skilltag_create'),
    # path('skill-tags/<int:pk>/update/', views.SkillTagUpdateView.as_view(), name='skilltag_update'),
    # path('skill-tags/<int:pk>/delete/', views.SkillTagDeleteView.as_view(), name='skilltag_delete'),
    
    # Оптимизированные views
    path('optimized/', views.OptimizedResumeListView.as_view(), name='optimized_resume_list'),
    path('resume/<int:pk>/optimized/', views.resume_detail_optimized, name='resume_detail_optimized'),
]