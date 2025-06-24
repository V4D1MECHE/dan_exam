from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Resume, Skill, WorkExperience, Education, Contact, Language, Certificate, Award, Recommendation
from .serializers import (
    ResumeSerializer, ResumeListSerializer, SkillSerializer, 
    WorkExperienceSerializer, EducationSerializer, ContactSerializer,
    LanguageSerializer, CertificateSerializer, AwardSerializer, RecommendationSerializer
)
from .filters import (
    ResumeFilter, SkillFilter, WorkExperienceFilter, EducationFilter,
    ContactFilter, LanguageFilter, CertificateFilter, AwardFilter
)


class ResumeListCreateAPIView(generics.ListCreateAPIView):
    """Список всех публичных резюме и создание нового резюме"""
    queryset = Resume.objects.filter(is_public=True).select_related('user')
    serializer_class = ResumeListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ResumeFilter
    search_fields = ['title', 'summary', 'city', 'user__first_name', 'user__last_name']
    ordering_fields = ['created_at', 'updated_at', 'salary_from', 'salary_to', 'title']
    ordering = ['-updated_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ResumeSerializer
        return ResumeListSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ResumeDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Детальная информация о резюме"""
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ResumeFilter
    
    def get_queryset(self):
        queryset = Resume.objects.select_related('user').prefetch_related(
            'contacts', 'work_experiences', 'educations', 'skills', 
            'languages', 'certificates', 'awards', 'recommendations'
        )
        
        if self.request.user.is_authenticated:
            return queryset.filter(user=self.request.user)
        else:
            return queryset.filter(is_public=True)


class MyResumesAPIView(generics.ListAPIView):
    """Мои резюме (только для авторизованных пользователей)"""
    serializer_class = ResumeListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ResumeFilter
    search_fields = ['title', 'summary', 'city']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)


class SkillListAPIView(generics.ListAPIView):
    """Список всех навыков"""
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SkillFilter
    search_fields = ['name']
    ordering_fields = ['name', 'level', 'created_at']
    ordering = ['name']


@api_view(['GET'])
def resume_stats(request):
    """Статистика резюме"""
    total_resumes = Resume.objects.count()
    public_resumes = Resume.objects.filter(is_public=True).count()
    total_skills = Skill.objects.count()
    
    return Response({
        'total_resumes': total_resumes,
        'public_resumes': public_resumes,
        'total_skills': total_skills
    })


@api_view(['GET'])
def popular_skills(request):
    """Популярные навыки"""
    skills = Skill.objects.all()[:10]
    serializer = SkillSerializer(skills, many=True)
    return Response(serializer.data)


# CRUD для связанных моделей
class WorkExperienceListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = WorkExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = WorkExperienceFilter
    search_fields = ['company_name', 'position']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-start_date']
    
    def get_queryset(self):
        resume_id = self.kwargs['resume_id']
        return WorkExperience.objects.filter(resume_id=resume_id, resume__user=self.request.user)
    
    def perform_create(self, serializer):
        resume_id = self.kwargs['resume_id']
        resume = get_object_or_404(Resume, id=resume_id, user=self.request.user)
        serializer.save(resume=resume)


class WorkExperienceDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = WorkExperienceFilter
    
    def get_queryset(self):
        return WorkExperience.objects.filter(resume__user=self.request.user)


class ContactListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ContactFilter
    search_fields = ['value', 'label']
    ordering_fields = ['contact_type', 'is_primary', 'created_at']
    ordering = ['order', 'created_at']
    
    def get_queryset(self):
        resume_id = self.kwargs['resume_id']
        return Contact.objects.filter(resume_id=resume_id, resume__user=self.request.user)
    
    def perform_create(self, serializer):
        resume_id = self.kwargs['resume_id']
        resume = get_object_or_404(Resume, id=resume_id, user=self.request.user)
        serializer.save(resume=resume)


class ContactDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ContactFilter
    
    def get_queryset(self):
        return Contact.objects.filter(resume__user=self.request.user)