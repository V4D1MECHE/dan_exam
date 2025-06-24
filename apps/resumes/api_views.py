from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Resume, Skill, WorkExperience, Education, Contact, Language, Certificate, Award, Recommendation
from .serializers import (
    ResumeSerializer, ResumeListSerializer, SkillSerializer, 
    WorkExperienceSerializer, EducationSerializer, ContactSerializer,
    LanguageSerializer, CertificateSerializer, AwardSerializer, RecommendationSerializer
)


class ResumeListCreateAPIView(generics.ListCreateAPIView):
    """Список всех публичных резюме и создание нового резюме"""
    queryset = Resume.objects.filter(is_public=True).select_related('user')
    serializer_class = ResumeListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
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
    
    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)


class SkillListAPIView(generics.ListAPIView):
    """Список всех навыков"""
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


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
    
    def get_queryset(self):
        return WorkExperience.objects.filter(resume__user=self.request.user)


class ContactListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    
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
    
    def get_queryset(self):
        return Contact.objects.filter(resume__user=self.request.user)