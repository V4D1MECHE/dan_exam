from django.urls import path
from . import api_views
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def api_root(request):
    """API корневая страница"""
    return Response({
        'message': 'Karrton Resume API',
        'endpoints': {
            'resumes': '/api/resumes/',
            'my_resumes': '/api/my-resumes/',
            'stats': '/api/stats/',
            'skills': '/api/skills/',
            'popular_skills': '/api/popular-skills/',
        }
    })

urlpatterns = [
    # Корневая страница API
    path('', api_root, name='api_root'),
    
    # Основные API endpoints для резюме
    path('resumes/', api_views.ResumeListCreateAPIView.as_view(), name='api_resume_list'),
    path('resumes/<int:pk>/', api_views.ResumeDetailAPIView.as_view(), name='api_resume_detail'),
    path('my-resumes/', api_views.MyResumesAPIView.as_view(), name='api_my_resumes'),
    
    # Статистика и популярные навыки
    path('stats/', api_views.resume_stats, name='api_resume_stats'),
    path('skills/', api_views.SkillListAPIView.as_view(), name='api_skills'),
    path('popular-skills/', api_views.popular_skills, name='api_popular_skills'),
    
    # API для связанных моделей
    path('resumes/<int:resume_id>/work-experience/', api_views.WorkExperienceListCreateAPIView.as_view(), name='api_work_experience_list'),
    path('work-experience/<int:pk>/', api_views.WorkExperienceDetailAPIView.as_view(), name='api_work_experience_detail'),
    
    path('resumes/<int:resume_id>/contacts/', api_views.ContactListCreateAPIView.as_view(), name='api_contact_list'),
    path('contacts/<int:pk>/', api_views.ContactDetailAPIView.as_view(), name='api_contact_detail'),
]