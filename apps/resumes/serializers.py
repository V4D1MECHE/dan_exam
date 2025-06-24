from rest_framework import serializers
from .models import Resume, WorkExperience, Education, Skill, Language, Contact, Certificate, Award, Recommendation


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'contact_type', 'value']


class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = ['id', 'company', 'position', 'start_date', 'end_date', 'current', 'achievements']


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'institution', 'degree', 'specialization', 'graduation_year', 'gpa']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'level', 'color']


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'name', 'level']


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ['id', 'name', 'organization', 'issue_date', 'expiry_date', 'certificate_file']


class AwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Award
        fields = ['id', 'title', 'organization', 'date', 'description']


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = ['id', 'name', 'position', 'company', 'email', 'phone', 'text']


class ResumeSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(many=True, read_only=True)
    work_experiences = WorkExperienceSerializer(many=True, read_only=True)
    educations = EducationSerializer(many=True, read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    languages = LanguageSerializer(many=True, read_only=True)
    certificates = CertificateSerializer(many=True, read_only=True)
    awards = AwardSerializer(many=True, read_only=True)
    recommendations = RecommendationSerializer(many=True, read_only=True)
    
    class Meta:
        model = Resume
        fields = [
            'id', 'user', 'title', 'photo', 'city', 'salary_from', 'salary_to', 
            'currency', 'employment_type', 'summary', 'is_public', 'created_at', 'updated_at',
            'contacts', 'work_experiences', 'educations', 'skills', 'languages',
            'certificates', 'awards', 'recommendations'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


class ResumeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['id', 'title', 'city', 'salary_from', 'salary_to', 'currency', 'employment_type', 'created_at']